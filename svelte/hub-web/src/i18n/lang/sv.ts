import type { LocaleData } from "i18n";

export default {
  title: "Junction Hub",
  roles: {
    "reseller-admin": "Återförsäljare - administratör",
    "reseller-user": "Återförsäljare",
    "snowfall-admin": "Snowfall - administratör",
    "snowfall-user": "Snowfall",
  },
  words: {
    yes: "Ja",
    no: "Nej",
    help: "Hjälp",
    unknown: "Okänd",
  },
  actions: {
    logout: "Logga ut",
    continue: "Fortsätt",
    cancel: "Avbryt",
    reportAnIssue: "Felrapportera",
    click: "Klicka",
    goToLogin: "Gå till login",
    search: "Sök",
  },
  sentences: {
    priceChange: "Prisändring",
    priceChangeInfo:
      'Vi har upptäckt en prisändring; ursprungspriset var <strong class="typography body-medium bold">{originalPrice}</strong> och det nya priset är <strong class="typography body-medium bold">{newPrice}</strong>. Vill du fortsätta?',
    areYouSure: "Är du säker?",
    copiedToClipboard: "Kopierad till urklipp",
  },
  pages: {
    dashboard: {
      title: "Instrumentbräda",
      intro: "<strong>Välkommen till</strong><span>Junction Hub</span>",
    },
    help: {
      title: "Hjälp",
      pages: {
        privacyPolicy: {
          title: "Integritetspolicy",
          content: [
            {
              type: "p",
              html: "Vi tror på att skydda slutkundens integritet. Se vår integritetspolicy på (infoga hyperlänk till webbplatsens sekretesspolicy) och vänligen gör din integritetspolicy tillgänglig för slutkunden eftersom detta kommer att gälla för deras bokning.",
            },
            { type: "h2", html: "Skadeersättning" },
            {
              type: "p",
              html: "Du samtycker till att försvara oss och/eller våra respektive leverantörer och någon av deras tjänstemän, direktörer, anställda och agenter från och mot alla anspråk, orsaker till åtgärder, krav, återkrav, förluster, skadestånd, böter, straff eller andra kostnader eller utgifter av något slag eller slag, inklusive men inte begränsat till rimliga juridiska avgifter och redovisningsavgifter, som tas ut av tredje part som ett resultat av:",
            },
            {
              type: "ul",
              items: [
                "- Ditt brott mot detta avtal eller de dokument som hänvisas till häri;",
                "- Ditt brott mot någon lag eller tredje parts rättigheter; eller",
                "- Din användning av Booking Hub.",
              ],
            },
            { type: "h2", html: "Valutaomvandlare, pris och betalning" },
            {
              type: "p",
              html: "Priserna för resetjänster är dynamiska och kan ändras ofta när som helst. Prisändringar kommer inte att påverka bokningar som redan lämnats, förutom där det har skett ett uppenbart fel. Vi gör allt vi kan för att säkerställa att priserna vi visar är korrekta och tillgängliga. Snowfall tar inget ansvar för bokningar till ett felaktigt pris där felet rimligen var (eller borde ha varit) uppenbart vid bokningstillfället, eller på grund av Snowfalls underlåtenhet att iaktta rimlig försiktighet.",
            },
            {
              type: "p",
              html: "Priserna som visas via vår tjänst kan inkludera skatter. Sådana skatter kan inkludera belopp förknippade med mervärdesskatt, skatt på varor och tjänster, försäljningsskatt, uthyrningsskatt och andra skatter av liknande karaktär.",
            },
            {
              type: "p",
              html: "I vissa jurisdiktioner, där så är tillämpligt, kan slutkunden också vara ansvarig för att betala lokala skatter som åläggs av lokala skattemyndigheter (såsom stadsskatter eller turistskatter etc). Vi kommer att meddela dig om eventuella lokala skatter som kommer att betalas av slutkunden innan bokningen slutförs, där sådana skatter har meddelats oss av reseleverantören.",
            },
            {
              type: "p",
              html: "Beloppet för lokala skatter kan ändras mellan bokningsdatum och vistelsedatum. Om skatterna har ändrats vid resedatumet kan slutkunden bli skyldig att betala skatt till den högre skattesatsen.",
            },
            {
              type: "p",
              html: "Betalning sker endast direkt till Snowfall Limited på uppdrag av reseleverantören.",
            },
            {
              type: "p",
              html: "Reseleverantören kräver vanligtvis betalning i förskott; det kan tas eller förauktoriseras när bokningen görs, och det kommer vanligtvis inte att återbetalas. Innan du gör en bokning, vänligen notera de individuella bokningsvillkoren som gäller.",
            },
            {
              type: "p",
              html: "Vi kan komma att lagra slutkundens betalningsmetod för framtida transaktioner om du har fått deras medgivande att göra det.",
            },
            {
              type: "p",
              html: "Som nämnts ovan accepterar du de tillämpliga policyerna som visas i bokningsprocessen. Du hittar varje reseleverantörs avbokningspolicy och alla andra policyer (om ålderskrav, kort som accepteras etc.) i det finstilta och/eller i bekräftelsemejlet eller biljetten (om tillämpligt).",
            },
            {
              type: "p",
              html: "Eftersom du gör en bokning för någon annans räkning, accepterar du ansvaret för att erhålla deras tillstånd innan du ger oss deras personuppgifter.",
            },
            { type: "h2", html: "Avbokningar och återbetalningar" },
            {
              type: "p",
              html: "Avbokningsavgifterna som tillämpas på bokningen är föremål för den specifika policy som fastställts av respektive leverantör. Dessa avgifter kommer att variera beroende på leverantörens villkor och villkor, och vi ansvarar inte för deras beslut. Även om vi strävar efter att tillhandahålla korrekt och snabb återbetalningshantering tar vi inget ansvar för tredje parts leverantörs åtgärder eller policyer. Eventuella tvister eller problem relaterade till avbokningar, återbetalningar eller associerade avgifter ska lösas direkt med den enskilda leverantören.",
            },
            { type: "h2", html: "Kontouppsägning" },
            {
              type: "p",
              html: "Efter eget gottfinnande kan vi säga upp kontoinnehavare som anses vara upprepade intrång. Vi kan också efter eget gottfinnande begränsa åtkomsten till bokningshubben och/eller avsluta konton för användare som gör intrång i andras immateriella rättigheter, oavsett om det förekommer upprepade intrång eller inte.",
            },
            { type: "h2", html: "Allmänt" },
            {
              type: "p",
              html: "Om någon del av detta avtal visar sig vara ogiltig, olaglig eller omöjlig att verkställa, kommer giltigheten, lagligheten och verkställbarheten av de återstående bestämmelserna inte på något sätt att påverkas eller försämras. Vårt misslyckande eller försening med att upprätthålla någon bestämmelse i detta avtal vid något tillfälle avsäger oss inte vår rätt att genomdriva samma eller någon annan bestämmelse häri i framtiden. Detta avtal (och alla andra villkor som hänvisas till häri) utgör hela avtalet mellan dig och oss med avseende på bokningshubben och det ersätter all tidigare eller samtidig kommunikation och förslag, oavsett om det är elektroniskt, muntligt eller skriftligt, mellan slutkunden och oss med avseende på bokningshubben.",
            },
            {
              type: "p",
              html: "Tillgång till denna bokningshub är villkorad av ditt samtycke till att all information som finns i den och alla frågor som uppstår mellan dig och oss kommer att styras av lagarna i England och Wales. Det är också villkorat av ditt samtycke att varje tvist som uppstår mellan dig och oss kommer att vara föremål för den exklusiva jurisdiktionen för domstolarna i England och Wales.",
            },
            {
              type: "p",
              html: "Alla rättigheter som inte uttryckligen beviljas häri är förbehållna.",
            },
            { type: "h2", html: "Kontak" },
            {
              type: "p",
              html: 'Alla kommentarer, frågor och förfrågningar som rör vår användning av Din information ska riktas till <a href="mailto:legal@snowfalltravel.com">legal@snowfalltravel.com</a>',
            },
          ],
        },
      },
    },
    account: {
      title: "Kontoinställningar",
    },
    knowledgeHub: {
      title: "Kunskapshub",
    },
    pay: {
      pages: {
        activity: {
          title: "Aktivitet",
        },
        bills: {
          title: "Räkningar",
        },
      },
    },
    tripManagement: {
      pages: {
        book: {
          title: "Boka",
        },
        orders: {
          title: "Visa ordrar",
        },
      },
    },
  },
  ory: {
    formGroups: {
      default: "Standard",
      password: "Uppdatera lösenord",
      oidc: "OIDC",
      profile: "Allmänt",
      link: "Länk",
      code: "Kod",
      totp: "Tvåfaktorsautentisering",
      // eslint-disable-next-line camelcase
      lookup_secret: "Återställningskoder",
      webauthn: "Säkerhetsnycklar",
    },
  },
} satisfies LocaleData;
