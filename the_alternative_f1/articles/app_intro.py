import reflex as rx

article = {
    "title": "New App, Who Dis?",
    "blurb": "A short walkthrough of how to navigate the new app.",
    "content": [
        # Two paragraphs with bold, italics, underline, and highlighted text throughout
        rx.text(
            "Welcome to Season 5 of The Alternative F1's sim racing league, where racing meets integrity, or whatever Erick used to say. This season we have a new app with new UI. Because of that, the boss man figured I needed to walk all you numbskulls through how the app works. This feels really rudimentary...but I, the illustrious intern, have authored the following guide to the features that work now and the features that are coming soon to the app."
            "Below you can obviously see a screenshot of the app that you already used to get to this article...so step one complete, you learned how to open an article. You've earned your coveted 'I'm not an idiot' Alternative Merit Badge. Now really, below you can see the home page of the app which has a navigation bar at the bottom and all the league news right in your face. No more bs about missing an article or whatever. It is literally the easiest thing to find in the app.",
            "From left to right you have a few buttons you can select. First the Regulations and Settings button. You aren't going to read it anyway, but that is where you will find the official league regulations (aka the penalties you can get, talking to you Junior) and the settings the races are set to. Next to that you can find the All Time Statistics section which has all sorts of stats on who the best driver is (Nick), who the best constructor is (Mercedes), and soon a few more stats courtesy of the BoxBox bot. The center is the Alternative logo that sends you to the main homepage with the news on it. Yes the big round button is the home button. Yes we stole that from Apple circa June 2007, deal with it. To the right of the home button is the most important section of all, the season stats page. And to the right of that is a login button that doesn't work...yet...",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),

        #TODO INSERT SCREENSHOT OF HOMEPAGE

        rx.box(
            rx.image( #TODO UPDATE THIS
                src="/logo_with_black.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            rx.text(
                "Alright, so you made it to the Regulations and Settings page. Proud of you. On the side you will see these two buttons that let you switch between regs and settings. You will also notice, that you can scroll...ya know...like all apps have done since, well, apps were invented. Keep up boomer.",
                "You're gonna see sidebar buttons like that all over the place, so get used to it. Pretty much every major section has them.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
                margin_bottom="4",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.box(
            rx.image( #TODO UPDATE THIS
                src="/logo_with_black.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            rx.text(
                "Color me impressed, you are still reading this article. Shocking honestly. Alright so in the All Time Stats section the only real thing to know is that all the tables scroll left to right as well as top to bottom.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
                margin_bottom="4",
            ),
            width="100%",
            margin_bottom="4",
        ),

        rx.box(
            rx.image( #TODO UPDATE THIS
                src="/logo_with_black.png",
                width="100%",
                max_width="400px",
                border_radius="md",
                box_shadow="0 4px 12px rgba(0,0,0,0.4)"
            ),
            rx.text(
                "Truly, I am so impressed that you are still reading this. Since you're here, in the discord go and do me a favor. Just ask Joshua if he plans on hitting the pit wall in Austria again this year. Will ya do that for me? K, thanks.",
                "So you wanna see this season's standings, or heck you wanna see last year's or really any year before this. Well the good news is you can. That little arrow in the top left, yeah that one, click it, and bang you can select what season to view. After that the tabs are pretty much self-explanatory unless you eat rocks or something and can't spell. Now there is one fun feature that was added here in the update. The Driver Comparison tab now has a rookie toggle for Season 2 and onward. If you can't figure out why Season 2 and onward, maybe put the Crayons you're munching on down and touch some grass. Beyond that, the info here is business as usual just a little shinier than last year.",
                color="#E0E0E0",
                font_size="md",
                line_height="1.7",
                margin_bottom="4",
            ),
            width="100%",
            margin_bottom="4",
        ),
        
        rx.text(
            "To those who have made it this far, thank you. To those who did 'suck my balls mate' or whatever K-Mag said. Enjoy the new app, sometime soon I am sure you will hear all about the login feature, commenting on articles, and a few new stats the team is cooking up. But for now, I hope you don't crash in turn 1. No seriously, don't crash that early, it makes for boring memes.",
            color="#E0E0E0",
            font_size="md",
            line_height="1.7",
            margin_bottom="4",
        ),
    ],
    "image": "/logo_with_black.png",
    "author": "The Intern",
    "date": "June 24, 2026",
    "season": 0,
}
