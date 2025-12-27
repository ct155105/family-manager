"""
Recommendation History Database Module

Manages persistent state for family activity recommendations using Firestore.

Key Patterns Demonstrated:
1. State Abstraction: Agent logic doesn't know about Firestore details
2. Query-Optimized Schema: Designed for time-range queries
3. Error Resilience: Graceful degradation if database unavailable
4. Type Safety: Clear return types for agent consumption

Architecture:
    Agent (family_manager.py)
        ↓ calls get_recent_recommendations()
    State Manager (this file)
        ↓ queries Firestore
    Cloud Database

Teaching Note: This pattern allows you to swap storage backends
(JSON file, SQLite, etc.) without changing agent code.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


class RecommendationDatabase:
    """
    Manages recommendation history in Firestore.

    Pattern: Repository Pattern
    - Encapsulates all database operations
    - Provides clean interface to agent
    - Handles connection management
    """

    def __init__(self):
        """
        Initialize Firestore client using Application Default Credentials (ADC).

        Authentication Methods (SDK tries in order):
        1. GOOGLE_APPLICATION_CREDENTIALS env var (service account JSON)
        2. gcloud user credentials (from: gcloud auth application-default login)
        3. GCE metadata service (when running on Google Cloud)
        4. GKE workload identity (in Kubernetes)

        Environment Variables:
        - FIRESTORE_PROJECT_ID: Required for ADC (your GCP project ID)
        - GOOGLE_APPLICATION_CREDENTIALS: Optional (overrides ADC if set)

        Teaching Note: This pattern is called "Credential Chain" or "Default Credentials".
        The same code works across local dev, CI/CD, and cloud environments.
        Each environment provides credentials differently, but your code doesn't change.
        """
        # Get project ID - required for ADC since it's not embedded in user credentials
        # (Service account JSON contains project ID, but gcloud user creds don't)
        project_id = os.getenv('FIRESTORE_PROJECT_ID')

        if not project_id:
            raise ValueError(
                "FIRESTORE_PROJECT_ID not set. "
                "Please set it in .env to your GCP project ID.\n"
                "Example: FIRESTORE_PROJECT_ID=my-family-manager-project"
            )

        # Initialize Firestore client with ADC
        # Teaching Note: When no credentials parameter is passed, the SDK
        # automatically uses Application Default Credentials (ADC).
        # This is simpler AND more flexible than explicit credential loading.
        self.db = firestore.Client(project=project_id)

        # Collection name supports environment-based separation
        # Pattern: Environment-based collection switching
        # - Production: FIRESTORE_COLLECTION=recommendations (default)
        # - Testing: FIRESTORE_COLLECTION=recommendations_test
        # This keeps test data isolated from production data
        self.collection_name = os.getenv('FIRESTORE_COLLECTION', 'recommendations')

        print(f"🔥 Connected to Firestore project: {project_id} (collection: {self.collection_name})")

    def save_recommendation(
        self,
        raw_suggestions: str,
        venues_mentioned: List[str],
        events_mentioned: Optional[List[str]] = None,
        weather_conditions: Optional[str] = None
    ) -> str:
        """
        Save a new recommendation to the database.

        Args:
            raw_suggestions: Full text of agent's recommendations
            venues_mentioned: List of venue names mentioned
            events_mentioned: List of specific events mentioned (optional)
            weather_conditions: Weather context (optional)

        Returns:
            str: Document ID of saved recommendation

        Pattern: Write-through cache
        - Immediately persist to database
        - Return ID for potential rollback/update

        Teaching Note: In production, you might:
        - Add retry logic for transient failures
        - Use batched writes for multiple recommendations
        - Implement write-ahead logging
        """
        now = datetime.now()

        doc_data = {
            'timestamp': now,
            'date': now.strftime('%Y-%m-%d'),
            'venues_mentioned': venues_mentioned,
            'events_mentioned': events_mentioned or [],
            'weather_conditions': weather_conditions or '',
            'raw_suggestions': raw_suggestions,
            'created_by': 'family_manager_v1',
            'created_at': firestore.SERVER_TIMESTAMP  # Server-side timestamp
        }

        # Add document to collection
        doc_ref = self.db.collection(self.collection_name).add(doc_data)
        doc_id = doc_ref[1].id  # Returns (timestamp, DocumentReference)

        print(f"✅ Saved recommendation to Firestore: {doc_id}")
        return doc_id

    def get_recent_recommendations(self, days: int = 30) -> List[Dict]:
        """
        Retrieve recommendations from the last N days.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            List of recommendation dictionaries, ordered by timestamp (newest first)

        Pattern: Time-windowed query
        - Uses indexed timestamp field for efficiency
        - Limits data returned to agent context

        Teaching Note: Why limit to 30 days?
        - Keeps agent context focused
        - Reduces token usage
        - Recent recommendations more relevant
        - Older data can be archived/aggregated separately
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Query Firestore
        # Pattern: Chained query builder
        # Note: Using FieldFilter for modern Firestore SDK syntax
        docs = (
            self.db.collection(self.collection_name)
            .where(filter=FieldFilter('timestamp', '>=', cutoff_date))
            .order_by('timestamp', direction=firestore.Query.DESCENDING)
            .stream()
        )

        recommendations = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            recommendations.append(data)

        print(f"📚 Retrieved {len(recommendations)} recommendations from last {days} days")
        return recommendations

    def get_recently_visited_venues(self, days: int = 30) -> List[str]:
        """
        Get a list of venues mentioned in recent recommendations.

        This is the primary method called by the agent.

        Args:
            days: Number of days to look back

        Returns:
            List of unique venue names

        Pattern: Materialized query
        - Agent doesn't need full recommendation objects
        - Return just what's needed (venue names)
        - Reduces agent context size

        Teaching Note: This is "lazy loading" for agents
        - Agent asks: "What venues should I avoid?"
        - We return: ["Columbus Zoo", "Metro Parks"]
        - Agent never sees full recommendation documents (unless needed)
        """
        recent = self.get_recent_recommendations(days)

        # Flatten venues_mentioned arrays and deduplicate
        venues = set()
        for rec in recent:
            venues.update(rec.get('venues_mentioned', []))

        venue_list = sorted(list(venues))

        if venue_list:
            print(f"🏛️  Recently visited: {', '.join(venue_list)}")
        else:
            print("🏛️  No recent visits found")

        return venue_list


# Singleton instance
# Pattern: Singleton with lazy initialization
_db_instance: Optional[RecommendationDatabase] = None

def get_db() -> RecommendationDatabase:
    """
    Get or create the database instance.

    Pattern: Singleton Pattern
    - One database connection per application lifecycle
    - Avoids repeated authentication
    - Connection pooling handled by Firestore SDK

    Teaching Note: Why singleton here?
    - Database connections are expensive
    - Firestore client manages connection pool internally
    - Multiple instances would waste resources
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = RecommendationDatabase()
    return _db_instance


# Convenience functions for agent code
# Pattern: Facade Pattern - Simple interface over complex subsystem

def save_recommendation(
    raw_suggestions: str,
    venues_mentioned: List[str],
    events_mentioned: Optional[List[str]] = None,
    weather_conditions: Optional[str] = None
) -> str:
    """
    Save a recommendation (convenience function).

    Teaching Note: Why wrap the class method?
    - Agent code can call save_recommendation() directly
    - Don't need to manage database instance
    - Can swap implementation without changing agent code
    """
    db = get_db()
    return db.save_recommendation(
        raw_suggestions=raw_suggestions,
        venues_mentioned=venues_mentioned,
        events_mentioned=events_mentioned,
        weather_conditions=weather_conditions
    )


def get_recently_visited_venues(days: int = 30) -> List[str]:
    """
    Get recently visited venues (convenience function).

    This is what your agent will call in family_manager.py
    """
    db = get_db()
    return db.get_recently_visited_venues(days)


def get_recent_recommendations(days: int = 30) -> List[Dict]:
    """
    Get recent recommendations (convenience function).
    """
    db = get_db()
    return db.get_recent_recommendations(days)
