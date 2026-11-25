<!DOCTYPE html>
<html class="light" lang="nl">
<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <title>DEVENTER SLOEP - Inloggen</title>
    <!-- Material Symbols -->
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&amp;display=swap" rel="stylesheet">
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <!-- Tailwind Config -->
    <script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "surface-container-high": "#e8e8e8",
                        "cadet-grey": "#717C96",
                        "outline-variant": "#c5c6d0",
                        "on-tertiary-container": "#c9915d",
                        "on-tertiary": "#ffffff",
                        "signal-red": "#D0021B",
                        "on-primary": "#ffffff",
                        "surface-tint": "#4a5d8f",
                        "secondary-fixed-dim": "#c5c7c8",
                        "oxford-blue": "#1D3261",
                        "on-surface-variant": "#44464f",
                        "inverse-on-surface": "#f0f1f1",
                        "on-secondary-fixed-variant": "#454748",
                        "on-secondary-fixed": "#191c1d",
                        "on-primary-fixed": "#001946",
                        "secondary-fixed": "#e2e2e3",
                        "on-secondary": "#ffffff",
                        "tertiary-container": "#502b00",
                        "performance-green": "#27AE60",
                        "on-surface": "#1a1c1c",
                        "on-secondary-container": "#616364",
                        "outline": "#757780",
                        "tertiary-fixed": "#ffdcbf",
                        "surface": "#f9f9f9",
                        "surface-container-lowest": "#ffffff",
                        "surface-container": "#eeeeee",
                        "on-tertiary-fixed-variant": "#663d10",
                        "background": "#f9f9f9",
                        "primary": "#021c4b",
                        "surface-dim": "#dadada",
                        "surface-bright": "#f9f9f9",
                        "primary-fixed": "#dae2ff",
                        "on-primary-fixed-variant": "#314575",
                        "error-container": "#ffdad6",
                        "tertiary-fixed-dim": "#f7ba83",
                        "secondary-container": "#dfe0e1",
                        "primary-fixed-dim": "#b2c5fe",
                        "on-primary-container": "#889bd1",
                        "on-tertiary-fixed": "#2d1600",
                        "error": "#ba1a1a",
                        "tertiary": "#321900",
                        "surface-container-low": "#f3f3f4",
                        "secondary": "#5c5f60",
                        "primary-container": "#1d3261",
                        "surface-variant": "#e2e2e2",
                        "inverse-primary": "#b2c5fe",
                        "on-error": "#ffffff",
                        "on-background": "#1a1c1c",
                        "inverse-surface": "#2f3131",
                        "surface-container-highest": "#e2e2e2",
                        "on-error-container": "#93000a",
                        "silver-mist": "#D9DADB"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                    },
                    "spacing": {
                        "gutter": "16px",
                        "unit": "4px",
                        "container-margin": "24px",
                        "metric-gap": "32px"
                    },
                    "fontFamily": {
                        "display-metrics": ["Inter"],
                        "headline-lg": ["Inter"],
                        "headline-lg-mobile": ["Inter"],
                        "body-lg": ["Inter"],
                        "label-sm": ["Inter"],
                        "headline-md": ["Inter"],
                        "label-md": ["Inter"],
                        "body-md": ["Inter"]
                    },
                    "fontSize": {
                        "display-metrics": ["48px", { "lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "700" }],
                        "headline-lg": ["32px", { "lineHeight": "40px", "letterSpacing": "-0.01em", "fontWeight": "700" }],
                        "headline-lg-mobile": ["24px", { "lineHeight": "32px", "fontWeight": "700" }],
                        "body-lg": ["18px", { "lineHeight": "28px", "fontWeight": "400" }],
                        "label-sm": ["12px", { "lineHeight": "16px", "fontWeight": "500" }],
                        "headline-md": ["20px", { "lineHeight": "28px", "fontWeight": "600" }],
                        "label-md": ["14px", { "lineHeight": "20px", "letterSpacing": "0.05em", "fontWeight": "600" }],
                        "body-md": ["16px", { "lineHeight": "24px", "fontWeight": "400" }]
                    }
                }
            }
        }
    </script>
    <style>
        body {
            min-height: max(884px, 100dvh);
        }
    </style>
</head>
<body class="bg-surface-container-lowest min-h-screen flex flex-col justify-center items-center px-container-margin text-on-surface antialiased">
    <!-- Main Login Container -->
    <main class="w-full max-w-[400px] flex flex-col items-center">
        <!-- Branding Header -->
        <header class="flex flex-col items-center mb-10 w-full text-center">
            <div class="h-16 w-16 mb-4 rounded-full bg-surface-container flex items-center justify-center text-oxford-blue">
                <span class="material-symbols-outlined text-[32px]" style="font-variation-settings: 'FILL' 1;">directions_boat</span>
            </div>
            <h1 class="font-headline-lg-mobile text-headline-lg-mobile md:font-headline-lg md:text-headline-lg text-oxford-blue tracking-wider uppercase">BRUG TOT BRUG</h1>
            <p class="font-body-md text-body-md text-cadet-grey mt-2">Log in om je prestaties te bekijken</p>
        </header>

        <#if message?has_content>
            <div class="mb-4 w-full p-4 rounded border ${message.type == 'error'?string('bg-error-container border-signal-red text-signal-red', 'bg-surface-container border-silver-mist text-oxford-blue')}">
                ${kcSanitize(message.summary)?no_esc}
            </div>
        </#if>

        <!-- Login Form -->
        <form id="kc-form-login" onsubmit="login.disabled = true; return true;" action="${url.loginAction}" class="w-full flex flex-col gap-6" method="post">
            <!-- Email Input Group -->
            <div class="flex flex-col gap-2">
                <label class="font-label-md text-label-md text-oxford-blue" for="username"><#if !realm.loginWithEmailAllowed>Gebruikersnaam<#elseif !realm.registrationEmailAsUsername>Gebruikersnaam of E-mailadres<#else>E-mailadres</#if></label>
                <div class="relative">
                    <input class="w-full h-12 px-4 bg-surface-container-lowest border border-silver-mist rounded text-on-surface font-body-md text-body-md placeholder:text-cadet-grey focus:outline-none focus:border-oxford-blue focus:ring-1 focus:ring-oxford-blue transition-colors" 
                           id="username" name="username" value="${(login.username!'')}" placeholder="roeier@deventersloep.nl" required="" type="text" autofocus autocomplete="username">
                </div>
            </div>
            
            <!-- Password Input Group -->
            <div class="flex flex-col gap-2">
                <div class="flex justify-between items-center">
                    <label class="font-label-md text-label-md text-oxford-blue" for="password">Wachtwoord</label>
                    <#if realm.resetPasswordAllowed>
                        <a class="font-label-sm text-label-sm text-oxford-blue hover:text-surface-tint transition-colors" href="${url.loginResetCredentialsUrl}">Wachtwoord vergeten?</a>
                    </#if>
                </div>
                <div class="relative">
                    <input class="w-full h-12 px-4 bg-surface-container-lowest border border-silver-mist rounded text-on-surface font-body-md text-body-md placeholder:text-cadet-grey focus:outline-none focus:border-oxford-blue focus:ring-1 focus:ring-oxford-blue transition-colors" 
                           id="password" name="password" placeholder="••••••••" required="" type="password" autocomplete="current-password">
                </div>
            </div>

            <!-- Submit Button -->
            <button id="kc-login" class="w-full h-12 mt-2 bg-oxford-blue text-on-primary font-label-md text-label-md rounded flex items-center justify-center gap-2 hover:bg-primary-container transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-oxford-blue active:scale-[0.98]" name="login" type="submit">
                <span class="">Inloggen</span>
                <span class="material-symbols-outlined text-[20px]">login</span>
            </button>
        </form>

        <#if realm.password && realm.registrationAllowed && !registrationDisabled??>
            <!-- Sign Up Link -->
            <div class="mt-8 pt-6 border-t border-silver-mist w-full text-center">
                <p class="font-body-md text-body-md text-cadet-grey">
                    Nog geen account? 
                    <a class="font-label-md text-label-md text-oxford-blue hover:text-surface-tint ml-1 transition-colors" href="${url.registrationUrl}">Registreren</a>
                </p>
            </div>
        </#if>
    </main>
</body>
</html>
