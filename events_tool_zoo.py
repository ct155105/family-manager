from bs4 import BeautifulSoup

def parse_events(html):
    soup = BeautifulSoup(html, "html.parser")
    
    results = []
    
    ## PARSER CODE HERE ##
    # The relevant event listings are under:
    # <div class="views-element-container ... block-views-blockevents-block-2" ...>
    # Inside: <div class="view-content"> and each event is <div class="item">

    event_container = soup.find("div", class_="views-element-container", id="block-views-block-events-block-2")
    if not event_container:
        return results  # No events found
    
    view_content = event_container.find("div", class_="view-content")
    if not view_content:
        return results

    items = view_content.find_all("div", class_="item")
    
    # We'll use these as defaults since the events are for "Columbus Zoo and Aquarium"
    default_venue = "Columbus Zoo and Aquarium"
    default_address = "4850 Powell Rd, Powell, OH 43065"  # public address for the zoo

    for item in items:
        event = {}
        
        # 1. Title
        a_tag = item.find("a", class_="wrap")
        event['title'] = a_tag['title'].strip() if a_tag and a_tag.has_attr('title') else ''

        # 2. Date/Time / End Time
        # <h4>JUL 31 - OCT 5</h4> or other variants
        h4 = item.find("h4")
        date_text = h4.get_text(" ", strip=True) if h4 else ""
        # By default, assign everything to date_time, and split on '-' or '&'.
        # Examples: "JUN 29 & 30", "JUL 31 - OCT 5", "JUN 30 - JUL 4", "AUG 17 - 18", "WEEKENDS Oct 10 - 26"
        date_time = date_text.strip()
        end_time = ''
        import re

        # Try to split out ranges for end_time
        if '-' in date_time:
            left, right = date_time.split('-', 1)
            event['date_time'] = left.strip()
            event['end_time'] = right.strip()
        else:
            event['date_time'] = date_time
            event['end_time'] = ''
        
        # 3. Description (no dedicated field, but try to extract from img alt text or None)
        # Sometimes the logo image alt has meaningful context
        img_logo = item.find('span', class_='logo')
        description = ''
        if img_logo:
            img = img_logo.find('img')
            if img and img.has_attr('alt'):
                description = img['alt'].strip()
        event['description'] = description

        # 4. Venue (assume always Columbus Zoo and Aquarium unless info elsewhere)
        event['venue'] = default_venue

        # 5. Address (assume default)
        event['address'] = default_address

        # Add to results
        results.append(event)
    ## END PARSER CODE ##
    
    return results

html_content = """
<main role="main">
 <a id="main-content" tabindex="-1">
 </a>
 <div class="layout-content">
  <div class="region region-content">
   <div class="hidden" data-drupal-messages-fallback="">
   </div>
   <div class="block block-system block-system-main-block" id="block-tiki-content">
    <article about="/events" class="node node--type-page node--view-mode-full" data-history-node-id="53" typeof="schema:WebPage">
     <span class="rdf-meta hidden" content="Events" property="schema:name">
     </span>
     <div class="node__content">
     </div>
    </article>
   </div>
   <div class="views-element-container special block block-views block-views-blockspecial-content-block-1" id="block-views-block-special-content-block-1">
    <div>
     <div class="view view-special-content view-id-special_content view-display-id-block_1 js-view-dom-id-9cbea164248b997d83f5061c9cd10615e0572ac576e964f827c897b780c1b0af">
      <div class="view-content">
       <div class="views-row">
        <div class="views-field views-field-field-special-content">
         <div class="field-content">
          <div class="boxed red paragraph paragraph--type--double-block paragraph--view-mode--default">
           <div class="wrap">
            <div class="clearfix text-formatted field field--name-field-content field--type-text-long field--label-hidden field__item">
             <h2>
              unforgettable Events. Unbeatable Memories.
             </h2>
             <p>
              Looking for family-friendly things to do in Columbus? You’ve just found the city’s most magical event destination. The Columbus Zoo and Aquarium hosts a full lineup of can’t-miss experiences throughout the year—from glowing lanterns and trick-or-treat trails to millions of twinkling lights that bring the holiday season to life.
             </p>
             <p>
              Whether you're planning a weekend visit or building a staycation itinerary, our special events add something unforgettable to every season. Check out what’s coming up and start planning your next wild day out!
             </p>
            </div>
            <div class="clearfix text-formatted field field--name-field-content-two field--type-text-long field--label-hidden field__item">
             <figure class="caption caption-img" role="group">
              <img alt="tiger art at lantern festival " data-entity-type="file" data-entity-uuid="e60e128b-6eb1-4c9d-ba32-9379f77bec1a" height="1080" loading="lazy" src="/sites/default/files/inline-images/Social%20Square-Tiger%20Lanterns%203.png" width="1080"/>
              <figcaption>
               <em>
                The Columbus Zoo's
               </em>
               <a href="https://www.columbuszoo.org/lantern-festival">
                <em>
                 Lantern Festival
                </em>
               </a>
               <em>
                , happening July 31 thru October 5
               </em>
              </figcaption>
             </figure>
            </div>
           </div>
          </div>
         </div>
        </div>
       </div>
      </div>
     </div>
    </div>
   </div>
   <div class="views-element-container block block-views block-views-blockgallery-images-block-1" id="block-views-block-gallery-images-block-1">
    <div>
     <div class="flex-view tight gallery lg-3 sm-2 view view-gallery-images view-id-gallery_images view-display-id-block_1 js-view-dom-id-85c5c3065fb47f683fed1efd5939dadb94df95f64a9e87a7b5762d7aca404db7">
     </div>
    </div>
   </div>
   <div class="views-element-container flex-view lg-4 md-3 sm-2 xs-1 events block block-views block-views-blockevents-block-2" id="block-views-block-events-block-2">
    <div>
     <div class="view view-events view-id-events view-display-id-block_2 js-view-dom-id-0aa4e0adb976587484c460b6cf2ada81a4b2fda8917eb54488a2154cc6ab8acb">
      <div class="view-header">
       <div class="key">
        <img alt="event icon key" src="/sites/default/files/assets/ui/ek-new.jpg"/>
       </div>
      </div>
      <div class="view-filters">
       <form accept-charset="UTF-8" action="/events" class="views-exposed-form bef-exposed-form" data-drupal-selector="views-exposed-form-events-block-2" id="views-exposed-form-events-block-2" method="get">
        <div class="form--inline clearfix">
         <div class="js-form-item form-item js-form-type-select form-type-select js-form-item-field-event-categories-target-id form-item-field-event-categories-target-id">
          <label for="edit-field-event-categories-target-id">
           Event Category
          </label>
          <select class="form-select" data-drupal-selector="edit-field-event-categories-target-id" id="edit-field-event-categories-target-id" name="field_event_categories_target_id">
           <option selected="selected" value="All">
            - Any -
           </option>
           <option value="65">
            Job Fair
           </option>
           <option value="4">
            21+ Event
           </option>
           <option value="64">
            Members Only Event
           </option>
           <option value="3">
            Family Event
           </option>
           <option value="5">
            Sensory-Friendly Event
           </option>
           <option value="6">
            Separate Registration Required
           </option>
          </select>
         </div>
         <div class="js-form-item form-item js-form-type-select form-type-select js-form-item-field-parks-target-id form-item-field-parks-target-id">
          <label for="edit-field-parks-target-id">
           Associated Park
          </label>
          <select class="form-select" data-drupal-selector="edit-field-parks-target-id" id="edit-field-parks-target-id" name="field_parks_target_id">
           <option selected="selected" value="All">
            - Any -
           </option>
           <option value="56">
            Columbus Zoo
           </option>
           <option value="59">
            Safari Golf Club
           </option>
           <option value="58">
            The Wilds
           </option>
           <option value="57">
            Zoombezi Bay
           </option>
          </select>
         </div>
         <div class="form-actions js-form-wrapper form-wrapper" data-drupal-selector="edit-actions" id="edit-actions">
          <input class="button js-form-submit form-submit" data-drupal-selector="edit-submit-events" id="edit-submit-events" type="submit" value="Apply"/>
         </div>
        </div>
       </form>
      </div>
      <div class="view-content">
       <div class="item">
        <a class="wrap" href="/events/early-member-mornings" title="Early Member Mornings">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="Early Member Mornings with sunrise" height="1200" loading="lazy" src="/sites/default/files/2023-01/Early-Membeer-Mornings-logo.png" typeof="Image" width="1200"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/64" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-64">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Members Only Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           JUN 29 &amp; 30
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/military-family-days" title="Military Family Days">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="BEF logo" height="641" loading="lazy" src="/sites/default/files/assets/events/Military-Family-Days_Bob-Evans_lockup3.png" typeof="Image" width="1200"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/3" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-3">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Family Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           JUN 30 - JUL 4
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/run-wild-5k" title="RUN WILD 5K">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="Run Wild graphic" height="524" loading="lazy" src="/sites/default/files/assets/events/Run-Wild-logo_White-CZA.png" typeof="Image" width="1000"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/6" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-6">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Separate Registration Required
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           JUL 6
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/jack-hanna-legacy-cup" title="Jack Hanna Legacy Cup">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="logo" height="2543" loading="lazy" src="/sites/default/files/assets/events/JackHannaLegacyCup_Logo.png" typeof="Image" width="3325"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/6" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-6">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Separate Registration Required
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           JUL 14
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/early-member-mornings-0" title="Early Member Mornings">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="Early Member Mornings with sunrise" height="1200" loading="lazy" src="/sites/default/files/2023-01/Early-Membeer-Mornings-logo_0.png" typeof="Image" width="1200"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/64" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-64">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Members Only Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           JUL 27 &amp; 28
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/lantern-festival" title="Lantern Festival">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="graphic" height="4167" loading="lazy" src="/sites/default/files/assets/events/Lantern_Festival_Logo_Color_transparent_background.png" typeof="Image" width="4167"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/3" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-3">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Family Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
             <li>
              <div about="/taxonomy/term/6" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-6">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Separate Registration Required
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           JUL 31 - OCT 5
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/franklin-county-community-days-0" title="Franklin County Community Days">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="Franklin County Community Days with artistic skyline and animals" height="683" loading="lazy" src="/sites/default/files/2023-02/Franklin-County-Community-Days-logo_WHITE-TEXT_0.png" typeof="Image" width="1031"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/3" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-3">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Family Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           AUG 17 - 18
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/blind-deaf-and-deafblind-accessibility-day" title="Blind, Deaf, and DeafBlind Accessibility Day">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="Blind Deaf and Deafblind event graphic" height="209" loading="lazy" src="/sites/default/files/assets/events/Blind-deaf-accessibility-day-text-only_ver2.png" typeof="Image" width="467"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/3" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-3">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Family Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
             <li>
              <div about="/taxonomy/term/5" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-5">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Sensory-Friendly Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           SEP 7
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/untamed" title="Untamed">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="uNTAMED LOGO" height="497" loading="lazy" src="/sites/default/files/assets/events/Untamed_WHITE-yellow-eyes.png" typeof="Image" width="597"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/4" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-4">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                21+ Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
             <li>
              <div about="/taxonomy/term/6" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-6">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Separate Registration Required
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           SEP 19
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/boo-zoo" title="Boo at  the Zoo">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="Boo at the Zoo Logo" height="198" loading="lazy" src="/sites/default/files/2022-12/boo-logo.png" typeof="Image" width="295"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/3" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-3">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Family Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           WEEKENDS Oct 10 - 26
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/wildlights-member-night" title="Wildlights Member Night">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt='Wildlights efficiently powered by AEP Ohio Member Night with the phrase "Member Night" underneath' height="500" loading="lazy" src="/sites/default/files/assets/events/WILDLIGHTS_members-night.png" typeof="Image" width="774"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/64" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-64">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Members Only Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           Nov 20
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/wildlights" title="Wildlights">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="Wildlights" height="176" loading="lazy" src="/sites/default/files/2023-01/Wildlights_AEP_2022.png" typeof="Image" width="353"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/3" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-3">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Family Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           Nov 21 - Jan 4
          </h4>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/events/rendezoo" title="RendeZOO">
         <img src="/sites/default/files/assets/ui/new-bg.png"/>
         <span class="logo">
          <img alt="graphic" height="516" loading="lazy" src="/sites/default/files/assets/events/RendeZOO-transparent-lockup_edit.png" typeof="Image" width="1080"/>
         </span>
         <div class="content">
          <div class="categories">
           <div class="item-list">
            <ul>
             <li>
              <div about="/taxonomy/term/4" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-4">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                21+ Event
               </div>
               <div class="content">
               </div>
              </div>
             </li>
             <li>
              <div about="/taxonomy/term/6" class="taxonomy-term vocabulary-event-categories" id="taxonomy-term-6">
               <div class="field field--name-name field--type-string field--label-hidden field__item">
                Separate Registration Required
               </div>
               <div class="content">
               </div>
              </div>
             </li>
            </ul>
           </div>
          </div>
          <h4>
           MAY 30
          </h4>
         </div>
        </a>
       </div>
      </div>
     </div>
    </div>
   </div>
   <div class="views-element-container mega-menu block block-views block-views-blockmega-menu-block-1" id="block-views-block-mega-menu-block-1">
    <div>
     <div class="view view-mega-menu view-id-mega_menu view-display-id-block_1 js-view-dom-id-fe7a3170978f6b9ee3eb04417864fe490104e17f5da8672cb5efe65782dd8c00">
      <div class="view-content">
       <div class="item">
        <a class="wrap" href="/partners-conservation">
         <img alt="Mountain Gorilla" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/Rwanda%202022%2001730%20%28Gorilla%29%20-%20Grahm%20S.%20Jones%2C%20Columbus%20Zoo%20and%20Aquarium_2.jpg?h=78aab1d8&amp;itok=wab06udF" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Partners in Conservation
          </h2>
          <p>
           Learn about the Zoo’s financial commitment to holistic conservation efforts in Central Africa.
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/103" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-103">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Conservation
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="https://www.columbuszoo.org/donate">
         <img alt="Bald Eagle at the Columbus Zoo and Aquarium" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/Bald%20Eagle%20%28Cheyenne%29%209120%20-%20Grahm%20S.%20Jones%2C%20Columbus%20Zoo%20and%20Aquarium.jpg?h=ea95bb15&amp;itok=wd4ZxhKl" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Give to the Zoo
          </h2>
          <p>
           There are so many ways to donate!
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/103" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-103">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Conservation
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="https://www.columbuszoo.org/elephant-updates">
         <img alt="Columbus Zoo staff performing ultrasound on elephant" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/Asian%20Elephant%20%28Phoebe%29%209882%20-%20Grahm%20S.%20Jones%2C%20Columbus%20Zoo%20and%20Aquarium%20%281%29.jpg?h=ea95bb15&amp;itok=jSsamrad" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Asian Elephants
          </h2>
          <p>
           The Columbus Zoo has not one, but TWO baby Asian elephants on the way.
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/104" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-104">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Animals
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/everyday-actions">
         <img alt="children looking at manatee at the Columbus Zoo" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/Zookids%20%28Manatees%29%203640%20-%20Grahm%20S.%20Jones%2C%20Columbus%20Zoo%20and%20Aquarium.jpg?h=d537e520&amp;itok=OnXG9Apa" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Everyday Actions
          </h2>
          <p>
           Learn about actions YOU can take to protect endangered species like the manatees.
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/104" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-104">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Animals
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="https://reservations.columbuszoo.org/Info.aspx?EventID=506">
         <img alt="children looking at polar bear" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/summer%20camp.JPG?h=7ccb2969&amp;itok=5UKNLFKw" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Zoo Camps
          </h2>
          <p>
           Learn about day camps for Zoo enthusiasts ages 3 all the way to 7th grade!
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/105" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-105">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Learn
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="https://www.columbuszoo.org/educators">
         <img alt="zoo field trip" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/School%20Groups%208198%20-%20Grahm%20S.%20Jones%2C%20Columbus%20Zoo%20and%20Aquarium.jpg?h=05b5059c&amp;itok=oNtxf49v" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Educator Resources
          </h2>
          <p>
           Explore our curriculum-aligned programs, resources, and exclusive opportunities for educators.
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/105" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-105">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Learn
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/membership">
         <img alt="Family walking at the Columbus Zoo near Adventure Cove sign" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/030325Columbus%20Zoo%20and%20Aquarium476A7645.jpg?h=9329522c&amp;itok=ndG8NdqW" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Membership
          </h2>
          <p>
           Become a Zoo member!
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/106" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-106">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Support
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
       <div class="item">
        <a class="wrap" href="/volunteer">
         <img alt="Adult Volunteer" class="image-style-mega-menu-250-x-125-" height="125" loading="lazy" src="/sites/default/files/styles/mega_menu_250_x_125_/public/assets/featured/Stephanie%20Kim%207538%20-%20Grahm%20S.%20Jones%2C%20Columbus%20Zoo%20and%20Aquarium.jpg?h=2e7c44a8&amp;itok=u8Q1vYUg" typeof="Image" width="250"/>
         <div class="text">
          <h2>
           Volunteer
          </h2>
          <p>
           Volunteer at the Columbus Zoo and Aquarium!
          </p>
          <span>
           <img alt="arrow" src="/sites/default/files/assets/ui/arrow-btn.png"/>
          </span>
          <div class="group">
           <div about="/taxonomy/term/106" class="taxonomy-term vocabulary-mega-menu-section" id="taxonomy-term-106">
            <div class="field field--name-name field--type-string field--label-hidden field__item">
             Support
            </div>
            <div class="content">
            </div>
           </div>
          </div>
         </div>
        </a>
       </div>
      </div>
     </div>
    </div>
   </div>
  </div>
 </div>
 <aside class="layout-sidebar-second" role="complementary">
 </aside>
</main>
"""

parse_events(html_content)