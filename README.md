# ☁️ Felhős AI Asszisztens – Felhasználói Dokumentáció
Ez az alkalmazás egy saját hosztolású, felhőalapú mesterséges intelligencia asszisztens, amely a Google Gemini 1.5 Flash modelljére épül. Egyedi adatbázis-kezeléssel, multimodális képességekkel és beépített kódolási eszközökkel rendelkezik.

# 1. Belépés és Adatbázis (Fiókkezelés)
Az alkalmazás egy privát GitHub repót használ "Git as a Database" (adatbázis) jelleggel.

Regisztráció/Belépés: Az oldalsávon keresztül tudsz jelszóval védett fiókot létrehozni. A jelszavakat a rendszer biztonságosan, titkosítva (hashelve) tárolja.

Automatikus mentés: A csevegéseid minden AI válasz után láthatatlanul, automatikusan elmentődnek a privát felhődbe.

Előzmények kezelése: Az oldalsávon a "Mentett beszélgetéseid" legördülő menüből bármikor betöltheted a korábbi munkáidat, vagy a 🗑️ ikonnal véglegesen törölheted őket az adatbázisból. A ➕ gombbal azonnal tiszta lappal indíthatsz egy új chatet.

-----------------------
# 2. Multimédia és Fájlfeltöltés 📎
A csevegősáv felett található feltöltő modul segítségével az AI nemcsak olvasni, de látni is tud.

Képek (JPG, PNG): Fotózz le egy hibás áramkört, egy kézzel írt jegyzetet, vagy tölts fel egy screenshotot egy dashboardról, és az AI felismeri és kielemzi a képi elemeket.

Dokumentumok és Kód (PDF, TXT, PY, CSV): * Ha egyetemi szakirodalmat vagy dokumentációt töltesz fel, a rendszer a háttérben másodpercek alatt kiolvassa a PDF szövegét.

Kiválóan alkalmas adatelemzésre: tölts fel egy CSV fájlt (például egy adathalmazt a PM10, PM2.5 és NO koncentráció mérési adataival), és kérd meg, hogy foglalja össze vagy írjon hozzá feldolgozó szkriptet.
-------------------

# 3. Személyiségek (System Prompts) 🧠
Az oldalsávban egy legördülő menüből kiválaszthatod, hogy az AI milyen szakmai keretrendszerben gondolkodjon és válaszoljon.

Általános Asszisztens: Mindennapi feladatokhoz és beszélgetéshez.

Adatelemző és Python Guru: Ha Pandas, Numpy vagy Seaborn kódot szeretnél íratni a kutatásodhoz, és az optimális adatkezelés a cél.

Pénzügyi Matematika Szakértő: Kifejezetten portfólió kockázatkezeléshez (Beta, CAPM) vagy opcióárazáshoz (Black-Scholes, Binomiális fák). Szakszavakat és precíz képleteket használ.

Kíméletlen Kritikus (Lektor): Ha azt akarod, hogy egy megírt szövegedet vagy forráskódodat szigorúan átnézze, és rámutasson a legkisebb logikai hibákra is.
-------------------------

# 4. Élő Webes Keresés 🌐
Mivel az AI alaptudása egy adott dátumnál véget ér, az oldalsávban bekapcsolhatod a Webes Keresést.

Működése: Ha be van pipálva, a beküldött kérdésedre a rendszer a háttérben azonnal rákeres a weben a DuckDuckGo motorjával, és az aktuális, legfrissebb cikkekből és forrásokból dolgozza ki a pontos választ.
--------------------

# 5. Hangvezérlés (Diktafon) 🎤
Ha telefonról használod a felületet, vagy nincs kedved hosszan gépelni, használd a chatmező feletti mikrofon ikont.

Működése: A "Kattints ide és kezdj beszélni" gombra nyomva a böngésződ beépített beszédfelismerője meghallgatja a kérdésed (tökéletesen érti a magyart is), és gépelés nélkül, azonnal szöveggé alakítja azt az AI számára.
------------------------

# 6. Beépített Kód Futtató (Sandbox) 💻
Az adatelemzési és fejlesztési feladatok leggyorsabb eszköze.

Működése: Ha az AI a válaszában Python kódot generál neked, az automatikusan betöltődik az oldalsávban lévő Kód Futtató dobozba.

Használat: Bármikor beleszerkeszthetsz, és a ▶️ Kód Futtatása gombbal helyben le is futtathatod. A rendszer azonnal kiírja a számítás eredményét, vagy – probléma esetén – a pontos Python hibaüzenetet (Traceback), amit azonnal visszaküldhetsz a chatbe javításra. (Biztonságos virtuális környezetben fut, így nem tud kárt tenni a szerverben).
