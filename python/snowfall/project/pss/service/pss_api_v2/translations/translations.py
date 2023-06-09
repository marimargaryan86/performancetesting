from gettext import gettext as _

translations = {
    "tr": _("Round trip"),
    "return_trip": _("Return trip"),
    "refund": _("Refunded"),
    "er": _("One way"),
    "adult": _("Adult"),
    "senior": _("Senior"),
    "youth": _("Youth"),
    "child": _("Child (2-12)"),
    "childYoung": _("Child (2-12)"),
    "student": _("Student"),
    "infant": _("Infant"),
    "w_seat": _("Wheelchair seat"),
    "a_seat": _("Animal seat"),
    "24_seat": _("Assigned 24h before departure*"),
    "subject": _("Split Express booking confirmation - booking reference "),
    "cancel_tkt_subject": _(
        "Split Express cancellation confirmation - booking reference ",
    ),
    "cancel_booking_subject": _(
        "Split Express cancellation confirmation - booking reference ",
    ),
    "refund_booking_subject": _(
        "Split Express refund confirmation - booking reference ",
    ),
    "forgot_password_subject": _("Split Express - password reset"),
    "booking_reminder_subject": _("Reminder of your trip with Split Express!"),
    "commuter_card_subject": _("Split Express commuter card purchase - "),
    "new_account_subject": _("Welcome to Split Express!"),
    "new_account": _("Sub copy goes here"),
    "new_account_notife_text": _("Thanks for signing up with SplitExpress"),
    "new_account_message": _("Welcome on board!"),
    "account_first_name": _("First Name"),
    "account_surname": _("Surname"),
    "account_mobile_number": _("Mobile Number"),
    "account_email": _("Email"),
    "forgot_password_title": _("FORGOT PASSWORD"),
    "forgot_password_greeting": _("Hello"),
    "forgot_password_received": _(
        "We received a request to change the password on your account.",
    ),
    "forgot_password_link": _("CHANGE THE PASSWORD"),
    "forgot_password_ignore": _(
        "You can ignore this email if you do not want to change your password.",
    ),
    "forgot_password_problem": _("Problems changing the password?"),
    "forgot_password_problem_link": _(
        (
            "If the password could not be changed by clicking the button above, please"
            " cut out this link and paste it into the browser's address bar."
        ),
    ),
    "forgot_password_problem_still": _(
        (
            "If you still have a problem changing your password, get back to our"
            " customer service at"
        ),
    ),
    "forgot_password_or": _("or"),
    "activate_loyalty_subject": _("Congratulations and welcome to club Xpress!"),
    "deactivate_loyalty_subject": _(
        "Your club Xpress membership has been unsubscribed!",
    ),
    "booking_confirmation": _("BOOKING CONFIRMATION"),
    "cancellation_confirmation": _("CANCELLATION CONFIRMATION"),
    "cancellation_refund_confirmation": _("CANCELLATION AND REFUND CONFIRMATION"),
    "refund_confirmation": _("REFUND CONFIRMATION"),
    "thanks": _("Thank you for your booking!"),
    "cancellation_tkt_thanks": _("A ticket is now cancelled"),
    "cancellation_vehicle_thanks": _("A vehicle is now cancelled"),
    "refund_tkt_thanks": _("A ticket is now refunded"),
    "cancellation_and_refund_tkt_thanks": _("A ticket is now cancelled and refunded"),
    "cancellation_and_refund_vehicle_thanks": _(
        "A vehicle is now cancelled and refunded",
    ),
    "cancellation_booking_thanks": _("Your trip is now cancelled"),
    "refund_booking_thanks": _("Your payment was refunded"),
    "cancellation_and_refund_booking_thanks": _(
        "Your trip is now cancelled and payment refunded",
    ),
    "thanks_txt": _("This email contains all the information about your trip."),
    "cancellation_thanks_txt_title": _(
        "Repayment of Split Express travels are as follows:",
    ),
    "cancellation_thanks_txt_tkt": _(
        (
            "A FIX trip is refundable until 24 hours after the time of purchase, and"
            " the reservation less than 24 hours to departure, the trip is refundable"
            " up to 12 hours before departure. A FLEX or 1 CLASS PLUS trip is"
            " refundable until departure. A voucher will be reactivated according to"
            " the same rules."
        ),
    ),
    "cancellation_thanks_txt": _(
        (
            "Repayment is made through our payment provider Klarna. Repayment normally"
            " takes 3-5 business days if you used a credit card and if you have paid by"
            " invoice Klarna will send a separate e-mail with more information within 2"
            " business days. If you have got any questions, please contact <a"
            ' href="mailto:kundservice@snowfallexpress.se">Split Express customer'
            " service</a>."
        ),
    ),
    "top_info": _(
        (
            "<strong>Your Travel certificate – Identification (for us to see that you"
            " have a ticket)</strong><br>All you need to have with you aboard is a"
            " valid identification with picture.<br><br><strong>Travel information -"
            " Mail and SMS (to facilitate your trip)</strong><br>Your travel"
            " information will be sent via SMS and e-mail. The e-mail you receive at"
            " once, while your SMS is sent out the day before your trip. If you book"
            " close to departure your SMS and e-mail will be sent at"
            " once.<br><br><strong>Before your trip</strong><br>What can you bring with"
            ' you on vehicle? Which baggage rules apply?<br><a href="{{ web_url }}"'
            ' style="color: #000000 !important; text-decoration: underline'
            ' !important;">Learn more about the most common questions before your trip'
            " here.</a><br>"
        ),
    ),
    "top_info_corp_invoice": _(
        (
            "<strong>Monthly Invoice Company</strong> The invoice is sent to your"
            " chosen billing address at the end of the month with all trips during the"
            " same billing period."
        ),
    ),
    "top_info_short": _(
        (
            "<strong>Your Travel certificate – Identification (for us to see that you"
            " have a ticket)</strong><br>All you need to have with you aboard is a"
            " valid identification with picture."
        ),
    ),
    "travel_details_txt": _("TRAVEL DETAILS"),
    "booking_reference": _("Booking reference"),
    "traveler": _("Traveler"),
    "travelers": _("Travelers"),
    "outbound": _("DEPARTURE"),
    "travel_type": _("Travel type"),
    "seat": _("Seat"),
    "wagon": _("Wagon"),
    "add_on": _("Add on"),
    "addons": _("Addons"),
    "inbound": _("RETURN TRIP"),
    "price": _("Price"),
    "total_price": _("Total price"),
    "amount_refunded": _("Refunded"),
    "sek": _("€"),
    "vat": _("VAT"),
    "tax": _("Port tax"),
    "amount_short": _("st"),
    "24_seat_txt": _(
        (
            "* Seats are assigned at least 24 hours before departure. You will then"
            " receive an email with the details of the seat to the e-mail address used"
            " when booking."
        ),
    ),
    "bottom_info": _(
        (
            "Book your free Birka Cruise here: <a"
            ' href="https://goo.gl/nXckji">goo.gl/nXckji</a><br />Use the code:'
            " SASplitX"
        ),
    ),
    "manage_booking": _("MANAGE YOUR BOOKING"),
    "manage_booking_txt": _("If you want to manage your booking you can do it here:"),
    "manage_booking_link": _("{{ web_url }}my-booking/"),
    "cancelled": _("Cancelled"),
    "cancelled_traveler": _("CANCELLED TRAVELER"),
    "booking_confirmation_offer": _("OFFERS"),
    "booking_confirmation_offer_box_1_title": _("TRY UBER WHEN YOU ARRIVED"),
    "booking_confirmation_offer_box_1_txt1": _(
        (
            "Book a car to pick you up at the station, easy, safe and affordable. The"
            " payment is done through the app, no wallet, no cash. In co-operation with"
            " Uber, Split Express offers you the first ride, worth 150:-."
        ),
    ),
    "booking_confirmation_offer_box_1_txt2": _(
        (
            'Go to <a href="https://uber.com/app">uber.com/app</a> and use this code to'
            " utulise this offer and to book your first ride. You’ll also recieve this"
            " code"
            " by text message when you’re approaching your final destination if you"
            " prefer"
            " to book your taxi then. The taxi ride has to be made by August 15, 2016."
        ),
    ),
    "booking_confirmation_offer_box_1_txt3": _(
        (
            "This offer is valid in Stockholm and Gothenburg, worth 150 sek at one"
            " occasion and can not be split up into several rides. Split Express can"
            " not guarantee that there will be an Uber available when you reach your"
            " final destination. Valid for first time users for uberX and uberBLACK."
            " All drivers are registered taxidrivers with registered cars and fare"
            " meters."
        ),
    ),
    "booking_confirmation_offer_box_1_link_txt": _("SEARCH AND BOOK A TAXI"),
    "booking_confirmation_offer_box_1_link": _("http://www.sveataxi.se/sv#boka-taxi"),
    "booking_confirmation_offer_box_2_title": _("BOOK A HOTEL NOW"),
    "booking_confirmation_offer_box_2_txt": _(
        "Book a hotel in Gothenburg. Sleep comfortably at First Hotels.",
    ),
    "booking_confirmation_offer_box_2_link_txt": _("SEARCH AND BOOK A HOTEL"),
    "booking_confirmation_offer_box_2_link": _("http://www.firsthotels.se"),
    "infant_info": _(
        (
            "<strong>Good to know for those traveling with small"
            " children:</strong><br>You have not booked any extra seat for your"
            " child.<br><br>Baby food is available for purchase in the cafe, but it is"
            " of course alright to bring your own.<br><br>Toilet with baby changing"
            " facilities are available in car [nearest-toilet-wagon].<br><br>Stroller"
            " may be included, subject to availability. The stroller can be placed in"
            " the luggage racks by the doors or folded and placed in the luggage rack"
            " above your seat."
        ),
    ),
    "stroller_info": _(
        (
            "<strong>Extra: Stroller</strong><br>Strollers may be brought on board."
            " Strollers are placed on the baggage shelves near the doors and folded and"
            " placed on the luggage rack above your seat. Strollers should be placed in"
            " Car D and if necessary, Car E and C.<p>Note that we cannot guarantee your"
            " stroller will be placed in the same car as you sit in. For security"
            " reasons children can not be seated/sleeping in stroller when the train is"
            " moving.</p>"
        ),
    ),
    "eurobonus_info": _(
        (
            "<strong>SAS EuroBonus</strong><br>This booking gives <strong>[eb-points]"
            " EuroBonus-points</strong> to every traveler who registered their"
            " EuroBonus-number for this trip.<br>Your SAS EuroBonus points will be"
            " awarded"
            " after your trip has been completed.<br>"
        ),
    ),
    "campaign_discount_long": _("Campaign discount"),
    "campaign_discount_short": _("Campaign"),
    "adult_discount_long": _("Campaign discount"),
    "adult_discount_short": _("Campaign"),
    "senior_discount_long": _("Senior discount"),
    "senior_discount_short": _("Senior"),
    "youth_discount_long": _("Youth discount"),
    "youth_discount_short": _("Youth"),
    "child_discount_long": _("Child discount"),
    "child_discount_short": _("Child"),
    "voucher_discount_long": _("Voucher"),
    "student_discount_long": _("Student discount"),
    "student_discount_short": _("Student"),
    "company_discount_long": _("Company agreement"),
    "rebook_discount_long": _("Rebooking"),
    "first_app_discount_long": _("First-time app discount"),
    "first_app_discount_short": _("First-time app"),
    "commuter_card_discount_long": _("Commuter card"),
    "plus_offer_top_title": _("TAXI OFFER!"),
    "plus_offer_title": _("1ST CLASS PLUS INCL. TAXI AND FOOD!"),
    "plus_offer_txt": _(
        (
            "When you book our 1ST CLASS PLUS roundtrip (applies bookings 1 Nov - 30"
            " Nov) you will receive a taxi check with a value of SEK 200 with Taxi"
            " Stockholm or Taxi Göteborg. The taxi Check is distributed in conjunction"
            " with your meal onboard (à SEK 100 per departure)."
        ),
    ),
    "ADDON_MEAL": _("Meal"),
    "ADDON_MEAL_BREAKFAST": _("Breakfast"),
    "ADDON_MEAL_BREAKFAST_PRE": _("Breakfast"),
    "ADDON_MEAL_LUNCH": _("Lunch"),
    "ADDON_MEAL_DINNER": _("Dinner"),
    "ADDON_MEAL_GLUTENFREE": _("Glutenfree"),
    "ADDON_MEAL_MILKFREE": _("Milkfree"),
    "ADDON_MEAL_VEGETARIAN": _("Vegetarian"),
    "ADDON_MEAL_SHRIMP_SANDWICH_PRE": _("Shrimp sandwich"),
    "ADDON_MEAL_CHICKEN_WRAP_PRE": _("Chicken wrap"),
    "ADDON_MEAL_TRI_SANDWICH_PRE": _("Triangular sandwich"),
    "ADDON_MEAL_CAESAR_SALAD_PRE": _("Classic Ceasar salad"),
    "ADDON_MEAL_QUINOA_SALAD_PRE": _("Vegan quinoa salad"),
    "ADDON_MEAL_VEGME_GLUTEN_MILK_FREE": _("Vegetarian wrap"),
    "ADDON_MEAL_BREAKFAST_PLUS": _("Breakfast"),
    "ADDON_MEAL_FULLMEAL_PLUS": _("Meal"),
    "ADDON_NEXT_SEAT_FREE": _("Next seat free"),
    "ADDON_STROLLER": _("Stroller"),
    "ADDON_STOCKHOLM_SODRA": _("SL ticket"),
    "ADDON_SELECT_SEAT": _("Choose your seat"),
    "referral_header": _("25% discount for you and your friends"),
    "referral_subheader": _("when you recommend Split Express"),
    "referral_description": _(
        (
            "When you encourage your friends to travel with the Split Express they will"
            " get <strong>25% discount</strong> at their first travel. You will also"
            " get <strong>25% discount</strong>!"
        ),
    ),
    "referral_button": _("Recommend Split Express"),
    "referral_link": _(" http://snowfall.se/en/refer/"),
    "travel_conditions_txt": _(
        (
            "Split EXPRESS (SWEDEN) AB´s and the passenger´s rights and obligations are"
            " governed by the provisions of the EUROPEAN PARLIAMENT AND COUNCIL"
            " REGULATION (EC) No 1371/2007 of 23 October 2007 on the rights and"
            " obligations of passengers, and Split EXPRESS (SWEDEN) AB´s General"
            " conditions for the transport of passengers by rail. Please contact <a"
            ' href="mailto:kundservice@snowfallexpress.se"'
            ' style="color:#ce0506;">kundservice@snowfallexpress.se</a> for questions'
            " and more information. These can be found on our website here:"
        ),
    ),
    "conditions_link": _(
        "http://snowfall.se/en/faq/6KS9jNas2QcCWsUuIUecmU/40YWEMvJOM8Yc8o6QAUuiA",
    ),
    "free_parking_top_title": _(
        "Together with the Split Express Citypark offers all customers",
    ),
    "free_parking_first_title": _("One day's free parking"),
    "free_parking_second_title": _("P-house centralen Göteborg"),
    "free_parking_text": _(
        (
            "If you need parking, you can print a <br> P-ticket which is valid for a"
            " whole day in the P-house Centralen Göteborg."
        ),
    ),
    "free_parking_btn_text": _("Open and print the P-ticket"),
    "free_parking_btn_link": _(
        (
            "https://gallery.mailchimp.com/f55af336338eb6d5f058f0b4d/"
            "files/snowfallx_citypark_centralen_goteborg_v5_maj.pdf"
        ),
    ),
    "same_day_change_info": _(
        (
            "<strong>Same day change</strong><br>When travelling with a 1 CLASS PLUS or"
            " FLEX ticket, we give you the opportunity to take the train before or"
            " after your original departure. Make your same day change with the Split"
            " Express app, simply log in and change your traveling details."
        ),
    ),
    "payment_option_invoice": _("Invoice"),
    "payment_option_company_invoice": _("Company invoice"),
    "train": _("train"),
    "phone": _("Phone"),
    "ticket_type": _("Type"),
    "name": _("Name"),
    "sj_annual_pass_info": _(
        (
            "<strong>Information about SJ annual pass trip</strong><br>You are required"
            " to carry your SJ annual pass onboard. This offer is non-transferable and"
            " for the offer to be valid, the passenger's name has to match name on the"
            " SJ annals pass. See you onboard!"
        ),
    ),
    "mtreurobonus_promo_register_link": _("www.snowfall.se/en/eurobonus/signup/"),
    "eurobonus_promo_header": _("EARN [eb-points] SAS EUROBONUS-POINTS!"),
    "eurobonus_promo_body": _(
        (
            "All new SAS EuroBonus members can earn 1000 Extrapoints in a welcome"
            " bonus, plus that you get [eb-product-points] points for your trip."
        ),
    ),
    "eurobonus_promo_register_link_text": _("SIGNUP TO EUROBONUS"),
    "rebooked": _("Rebooked"),
    "infant_seat": _(
        "Infant have no seat, but sitting in the lap of the other passengers.",
    ),
    "discount": _("Discount"),
    "relative_header": _("Closest relative"),
    "departure_text": _("departure"),
    "traveller": _("Traveller"),
    "telephone": _("Telephone"),
    "has_cancelled": _("has been cancelled"),
}
