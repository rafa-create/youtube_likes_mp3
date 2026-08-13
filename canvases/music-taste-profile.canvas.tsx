import {
  BarChart,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  PieChart,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasState,
} from "cursor/canvas";

type Person = "rafael" | "bram" | "duo";
type Mode = "analyse" | "creation";
type DuoTab = "overlap" | "roles" | "session" | "concepts";

const COL = "repeat(auto-fit, minmax(min(100%, 260px), 1fr))";
const COL_STATS = "repeat(auto-fit, minmax(min(100%, 140px), 1fr))";

/**
 * Indice de Gaytitude (IG) — blague « scientifique ».
 * Définition locale : affinité pour la musique soft / sensitive /
 * émotionnelle (souvent associée pop-culture à une écoute « gay-coded »
 * ou « sensitive female lead »), PAS une mesure d'orientation réelle.
 *
 * IG = 0.28·Mineur% + 0.22·SoftVocals + 0.20·ArtistesSensibles
 *    + 0.15·MoodMélancolique + 0.15·(100 − ClubHard)
 */
const GAYTITUDE = {
  rafael: {
    score: 81,
    label: "Très sensitive-pop",
    components: [
      { name: "Mode mineur (58%)", pts: 16.2, why: "423/726 pistes mineures — couleur introspective" },
      { name: "Soft vocals / piano / chanson", pts: 18.5, why: "Voix 108 + piano 49 + FR chanson 33 + neo-classical 44" },
      { name: "Artistes sensibles", pts: 17.2, why: "Sia, Pomme, HAEVN, Tom Odell, Alec Benjamin, Sheeran…" },
      { name: "Moods mélancoliques", pts: 15.0, why: "Intime/sombre + électro-mélancolie ≈ 45% des quadrants" },
      { name: "Anti-club (100−hard)", pts: 14.1, why: "EDM présent mais pas dominant vs émotion midtempo" },
    ],
  },
  bram: {
    score: 57,
    label: "Chill sensible, pas drama-pop",
    components: [
      { name: "Soft acoustic / intimacy", pts: 18.0, why: "Guitare + voix soft = cœur Chill (Johnson, Bahamas, Mayer)" },
      { name: "Artistes sensibles", pts: 11.0, why: "Mayer / Froukje / soft alt — mais Jack Johnson = beach-bro chill" },
      { name: "Tempo lent émotionnel", pts: 14.0, why: "~90 BPM → écoute corporelle douce, pas flex" },
      { name: "Blues/soul vulnerability", pts: 8.0, why: "Keb' Mo', Kiwanuka-adjacent pocket" },
      { name: "Anti-club", pts: 6.0, why: "Quasi zéro EDM — mais le 'dude with a guitar' baisse le score gay-coded" },
    ],
  },
  duo: {
    score: 69,
    label: "Duo émotionnellement bilingue",
    components: [
      { name: "Moyenne pondérée R/B", pts: 69.0, why: "0.6×81 (Rafael) + 0.4×57 (Bram) — Rafael tire vers le sensitive-pop" },
    ],
  },
} as const;

function GaytitudeBlock({
  who,
}: {
  who: "rafael" | "bram" | "duo";
}) {
  const g = GAYTITUDE[who];
  return (
    <Stack gap={12}>
      <Grid columns={COL_STATS} gap={12}>
        <Stat value={`${g.score}%`} label="Indice de Gaytitude" tone="info" />
        <Stat value={g.label} label="Lecture comique" />
      </Grid>

      <Callout tone="warning" title="Avertissement scientifique (très sérieux)">
        Cet indice est une blague méthodologique. Il estime une affinité pour la
        musique soft / sensitive / émotionnelle (stéréotype pop-culture « gay
        listening » ou « sensitive female / soft-male ballad »),{" "}
        <Text weight="semibold">pas</Text> une orientation sexuelle. Formule
        affichée ci-dessous — reproductible, discutable, et volontairement
        absurde.
      </Callout>

      <H3>Pourquoi ces stats ?</H3>
      <Text size="small" tone="secondary">
        On pondère des signaux déjà mesurés dans la playlist (mode mineur,
        artistes, mood, instruments, anti-club). Plus la musique privilégie
        vulnérabilité, voix douce, piano/guitare intimiste et mélancolie
        midtempo, plus l&apos;IG monte. Le club/EDM hard et le « beach bro
        acoustic » le font redescendre.
      </Text>

      <Table
        striped
        headers={["Composante", "Points /100", "Pourquoi ça compte ici"]}
        rows={g.components.map((c) => [c.name, String(c.pts), c.why])}
      />

      <Text size="small" tone="secondary">
        Formule : IG = 0.28·Mineur% + 0.22·SoftVocals + 0.20·ArtistesSensibles +
        0.15·MoodMélancolique + 0.15·(100−ClubHard) · arrondi comique à
        l&apos;entier le plus dramatique.
      </Text>
    </Stack>
  );
}

export default function MusicTasteProfile() {
  const [person, setPerson] = useCanvasState<Person>("person", "rafael");

  return (
    <Stack gap={18}>
      <Stack gap={6}>
        <H1>Rafael × Bram — playlists & création</H1>
        <Text tone="secondary">
          Analyse des goûts + briefs studio · Indice de Gaytitude (blague
          scientifique) · mobile & desktop
        </Text>
      </Stack>

      <Row gap={8} wrap>
        <Pill active={person === "rafael"} onClick={() => setPerson("rafael")}>
          Rafael
        </Pill>
        <Pill active={person === "bram"} onClick={() => setPerson("bram")}>
          Bram
        </Pill>
        <Pill active={person === "duo"} onClick={() => setPerson("duo")}>
          À deux
        </Pill>
      </Row>

      {person === "rafael" && <RafaelSection />}
      {person === "bram" && <BramSection />}
      {person === "duo" && <DuoSection />}

      <Text size="small" tone="secondary">
        Sources : likes YouTube Rafael (726 MP3, librosa) · Spotify Chill Bram
        (270 titres) · IG = blague pondérée sur signaux playlist
      </Text>
    </Stack>
  );
}

function ModeSwitch({
  mode,
  setMode,
}: {
  mode: Mode;
  setMode: (m: Mode) => void;
}) {
  return (
    <Row gap={8} wrap>
      <Pill active={mode === "analyse"} onClick={() => setMode("analyse")}>
        Analyse playlist
      </Pill>
      <Pill active={mode === "creation"} onClick={() => setMode("creation")}>
        Création artistique
      </Pill>
    </Row>
  );
}

/* ===================== RAFAEL ===================== */

function RafaelSection() {
  const [mode, setMode] = useCanvasState<Mode>("rafael-mode", "creation");
  return (
    <Stack gap={16}>
      <Grid columns={COL_STATS} gap={12}>
        <Stat value="776" label="Likes YT" />
        <Stat value="726" label="MP3 analysés" />
        <Stat value="~118" label="BPM médian" tone="info" />
        <Stat value="81%" label="Gaytitude IG" />
      </Grid>
      <ModeSwitch mode={mode} setMode={setMode} />
      {mode === "analyse" ? <RafaelAnalyse /> : <RafaelCreation />}
    </Stack>
  );
}

function RafaelAnalyse() {
  return (
    <Stack gap={18}>
      <Callout tone="info" title="Verdict playlist Rafael">
        Goût large mais centré : pop / électro-mélancolie midtempo, voix avant
        tout, mineur dominant, anglais + poche FR (Pomme…). Tempo confort ~118
        BPM. Les suites vi–IV–I–V (et rotations) structurent l&apos;écoute.
      </Callout>

      <H2>Indice de Gaytitude</H2>
      <GaytitudeBlock who="rafael" />

      <H2>Couverture & signal</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Mode (726 pistes)</CardHeader>
          <CardBody>
            <PieChart
              data={[
                { label: "Mineur", value: 423 },
                { label: "Majeur", value: 303 },
              ]}
            />
            <Text size="small" tone="secondary">
              58% mineur · chroma Krumhansl
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>BPM (buckets)</CardHeader>
          <CardBody>
            <BarChart
              categories={["<80", "80–100", "100–120", "120–140", "140+"]}
              series={[{ name: "Pistes", data: [54, 145, 126, 175, 117] }]}
              height={200}
            />
            <Text size="small" tone="secondary">
              Médiane 117.5 · P25–P75 96–136 · source accords+BPM
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Artistes récurrents (titres)</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "Nightcore",
                "Sia",
                "Alan Walker",
                "HAEVN",
                "Ed Sheeran",
                "Pomme",
                "Lost Frequencies",
                "Milky Chance",
              ]}
              series={[{ name: "Mentions", data: [15, 13, 7, 7, 7, 6, 5, 5] }]}
              height={260}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Signaux de style (titres)</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "electronic / EDM",
                "piano / neo-classical",
                "pop",
                "french pop / chanson",
                "folk / acoustic",
                "cinematic",
                "ambient / chill",
              ]}
              series={[{ name: "Hits", data: [45, 44, 43, 33, 29, 21, 14] }]}
              height={260}
            />
            <Text size="small" tone="secondary">
              Hors « autre / non classé » (572)
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Tonalités fréquentes</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "A minor",
                "G minor",
                "C major",
                "C# minor",
                "B minor",
                "D minor",
              ]}
              series={[{ name: "Pistes", data: [57, 47, 43, 40, 38, 37] }]}
              height={220}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Instruments (heuristique titres)</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={["voix", "synth", "piano", "guitare", "cordes"]}
              series={[{ name: "Taggés", data: [108, 71, 49, 31, 24] }]}
              height={220}
            />
            <Text size="small" tone="secondary">
              Voix 37.6% des titres taggés · 544 non taggés
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <H2>Mood & clusters</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Quadrants mood</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "équilibré / mid",
                "intime / sombre",
                "électro-mélancolie",
                "uplift / dance",
                "doux / lumineux",
              ]}
              series={[{ name: "Pistes", data: [183, 165, 159, 122, 97] }]}
              height={220}
            />
            <Text size="small" tone="secondary">
              Énergie moy. 0.54 · valence moy. 0.47
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Clusters de goût</CardHeader>
          <CardBody>
            <Table
              headers={["Cluster", "Part", "BPM", "% min"]}
              rows={[
                ["Équilibré midtempo", "32%", "109", "72%"],
                ["Uplift / dance", "24%", "137", "0%"],
                ["Électro mélancolique", "24%", "142", "100%"],
                ["Intime / sombre", "20%", "77", "58%"],
              ]}
            />
          </CardBody>
        </Card>
      </Grid>

      <H2>Harmonie détectée (617/703 filtrées)</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Suites absolues</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "Cm-G#-D#-A#",
                "G#-D#-A#-Cm",
                "A#-Cm-G#-D#",
                "G-D-A-Bm",
                "D-A-Bm-G",
                "C#m-A-E-B",
              ]}
              series={[{ name: "Occurrences", data: [21, 19, 19, 18, 17, 15] }]}
              height={240}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Degrés romains</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "vi-IV-I-V",
                "IV-I-V-vi",
                "I-V-vi-IV",
                "V-vi-IV-I",
                "I-i-I-i",
                "i-bVI-bVII-i",
              ]}
              series={[{ name: "Occurrences", data: [102, 90, 76, 69, 53, 47] }]}
              height={240}
            />
            <Text size="small" tone="secondary">
              Top 4 = rotations du même cycle pop
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <H3>Langues (heuristique titres, analyse accords)</H3>
      <BarChart
        horizontal
        categories={["en", "inconnu", "fr", "instrumental", "es"]}
        series={[{ name: "Pistes", data: [330, 160, 81, 41, 5] }]}
        height={180}
      />

      <Table
        striped
        stickyHeader
        headers={["Exemple piste", "Suite", "BPM", "Lang", "Key"]}
        rows={[
          ["Kid Francescoli — Moon", "G-Bm-D-G", "118", "en", "Bm"],
          ["Alec Benjamin — Devil Doesn't Bargain", "Cm-G#-D#-A#", "~118", "en", "D#"],
          ["Loner Deer — Joline", "Cm-D#-A#-Fm", "92", "en", "A#"],
          ["Billie Eilish — True Blue", "D-Am-C-Em", "103", "?", "Am"],
          ["Einaudi — Nuvole Bianche", "Fm-C#-G#-D#", "123", "?", "G#"],
          ["Alan Walker — The Spectre", "C#m-A-E-B", "~121", "en", "E"],
        ]}
      />
    </Stack>
  );
}

function RafaelCreation() {
  return (
    <Stack gap={18}>
      <Callout tone="info" title="Brief studio Rafael — priorité #1">
        Écris une chanson EN autour de <Text weight="semibold">Cm–G#–D#–A#</Text>{" "}
        (vi–IV–I–V), tempo <Text weight="semibold">116–120 BPM</Text>, lead
        vocal + synth support. Les rotations G#–D#–A#–Cm / A#–Cm–G#–D# sont la
        même grille — change juste le point d&apos;entrée (verse vs chorus).
      </Callout>

      <H2>3 lanes de création</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader trailing={<Text size="small">#1</Text>}>
            Pop mineure brillante
          </CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">Cm – G# – D# – A#</Text>
              <Text size="small" tone="secondary">
                ~118 BPM · EN · D# major · voix + pad
              </Text>
              <Text size="small">
                Hook sur D# ou A# · couplet plus sombre sur Cm. Valide 8 barres
                en boucle avant les paroles.
              </Text>
              <Text size="small" tone="secondary">
                Angle lyric : distance / nuit / désir contenu (Sia–Walker vibe)
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Text size="small">#2</Text>}>
            Pop / folk D
          </CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">G – D – A – Bm</Text>
              <Text size="small" tone="secondary">
                ~112 BPM · EN · D major · plus ouvert
              </Text>
              <Text size="small">
                Refrain anthem, couplet Bm. Bon pour guitare + stacks vocaux.
              </Text>
              <Text size="small" tone="secondary">
                Angle lyric : route / promesse / light after rain
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Text size="small">#3</Text>}>
            Électro uplift
          </CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">C#m – A – E – B</Text>
              <Text size="small" tone="secondary">
                ~121 BPM · 120–140 · EN · E major
              </Text>
              <Text size="small">
                Intro filter · drop léger sur E. Cousine G#m–E–B–F# si plus
                nightcore.
              </Text>
              <Text size="small" tone="secondary">
                Angle lyric : escape / neon / running
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <H2>Checklist DAW (45–90 min)</H2>
      <Table
        striped
        headers={["Étape", "Action concrète", "Critère OK"]}
        rows={[
          ["1. Tempo", "Click 118 BPM", "Body groove sans hard EDM"],
          ["2. Grille", "Cm–G#–D#–A# × 8 barres", "Boucle collante seule"],
          ["3. Voix guide", "Hum / oooh 2 motifs", "1 motif couplet, 1 refrain"],
          ["4. Pad / piano", "Pad mineur + piano sparse", "Ne pas masquer la voix"],
          ["5. Beat", "Kick soft + clap 2/4", "Moins dense que Walker club"],
          ["6. Langue", "EN draft 8 lignes", "FR = variante B / pont"],
          ["7. Arrangement", "Verse dry → chorus +1 couche", "Lift audible"],
        ]}
      />

      <H2>Structure song suggérée</H2>
      <Table
        striped
        headers={["Section", "Barres", "Accords", "Prod"]}
        rows={[
          ["Intro", "4–8", "Cm–G# (half)", "Pad + motif guitare/piano"],
          ["Verse 1", "8", "Cm–G#–D#–A#", "Voix dry, kick soft"],
          ["Pre", "4", "G#–D#–A#", "Build filter"],
          ["Chorus", "8", "D#–A#–Cm–G# (rotation)", "+clap, doubles voix"],
          ["Verse 2", "8", "comme V1", "+contre-mélodie"],
          ["Chorus 2", "8", "rotation", "+synth lead léger"],
          ["Bridge", "8", "Am-ish / half-time", "FR optionnel · strip"],
          ["Final chorus", "8–16", "plein", "Ad-libs · open end"],
        ]}
      />

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Prompts d&apos;écriture EN</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text size="small">« I keep the lights low so I don&apos;t see… »</Text>
              <Text size="small">« We talk in circles around the quiet… »</Text>
              <Text size="small">« Drive until the city forgets my name… »</Text>
              <Text size="small" tone="secondary">
                Thèmes qui matchent valence ~0.47 + mineur : tendresse + distance
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Variante FR (pont)</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text size="small">Garder la même grille · 4–8 barres FR</Text>
              <Text size="small">« On parle bas pour pas réveiller… »</Text>
              <Text size="small">« La ville oublie nos prénoms… »</Text>
              <Text size="small" tone="secondary">
                Pomme / Vitaa pocket — pas tout le titre en FR dès la v1
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="warning" title="Pièges Rafael">
        Trop de nightcore/EDM dès l&apos;intro (perd la mélancolie mid). Grille
        trop complexe (ton goût = 4 accords). FR partout trop tôt. Ton IG 81%
        dit : assume la vulnérabilité — n&apos;essaie pas de « durcir » pour
        faire plus macho, ça sonnera faux.
      </Callout>
    </Stack>
  );
}

/* ===================== BRAM ===================== */

function BramSection() {
  const [mode, setMode] = useCanvasState<Mode>("bram-mode", "creation");
  return (
    <Stack gap={16}>
      <Grid columns={COL_STATS} gap={12}>
        <Stat value="270" label="Titres Chill" />
        <Stat value="~90" label="BPM estimé" tone="info" />
        <Stat value="EN ~90%" label="Langue" />
        <Stat value="57%" label="Gaytitude IG" />
      </Grid>
      <ModeSwitch mode={mode} setMode={setMode} />
      {mode === "analyse" ? <BramAnalyse /> : <BramCreation />}
    </Stack>
  );
}

function BramAnalyse() {
  return (
    <Stack gap={18}>
      <Callout tone="info" title="Verdict playlist Bram (Spotify Chill)">
        Catalogue chill / island-folk + poche alt soft contemporaine. Jack
        Johnson domine, puis Bobby Alu / Bahamas / Mayer. Anglais massif.
        Densité basse, guitare, voix proche — pas de club EDM.
      </Callout>

      <H2>Indice de Gaytitude</H2>
      <GaytitudeBlock who="bram" />

      <H2>Artistes & poches</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Top artistes (270 titres)</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "Jack Johnson",
                "Bobby Alu",
                "Bahamas",
                "Frankenreiter",
                "John Mayer",
                "Bonga",
                "Loyle Carner",
                "Sido",
                "Dominic Fike",
                "Froukje",
              ]}
              series={[{ name: "Titres", data: [12, 5, 4, 3, 3, 3, 3, 3, 3, 3] }]}
              height={300}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Poches de style</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "chill / soft alt",
                "acoustic island",
                "hip-hop soft",
                "world / afro",
                "blues / soul",
              ]}
              series={[{ name: "Signal", data: [120, 34, 15, 12, 12] }]}
              height={240}
            />
            <Text size="small" tone="secondary">
              Heuristique artistes · pas tagging audio
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Langue</CardHeader>
          <CardBody>
            <PieChart
              data={[
                { label: "EN", value: 242 },
                { label: "Autres", value: 28 },
              ]}
            />
            <Text size="small" tone="secondary">
              ~90% anglais · poche NL/DE/world
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Instruments probables</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={["guitare", "voix", "harmonica", "ukulele/perc", "piano"]}
              series={[{ name: "Poids relatif", data: [55, 40, 12, 10, 8] }]}
              height={200}
            />
          </CardBody>
        </Card>
      </Grid>

      <H2>Tempo & densité (profil curatoriel)</H2>
      <Table
        striped
        headers={["Zone BPM", "Présence", "Rôle dans le goût"]}
        rows={[
          ["<80 ballade", "élevée", "intimité, blues soft, piano"],
          ["80–100 mid lent", "dominante", "cœur Chill / island"],
          ["100–120 pop", "faible", "alt soft / Fike edge"],
          ["120+", "rare", "hors centre — à éviter en v1"],
        ]}
      />

      <H3>Références d&apos;écoute (analyse → oreille)</H3>
      <Table
        striped
        headers={["Titre", "Pourquoi c’est central"]}
        rows={[
          ["Jack Johnson — Banana Pancakes", "Tempo + fingerstyle + EN soft"],
          ["Donavon Frankenreiter — Big Wave", "Groove island, ouverture"],
          ["John Mayer — Slow Dancing…", "Ballade émotionnelle C/G"],
          ["Bahamas / Bobby Alu", "Chill contemporain, espace"],
          ["Keb' Mo' / Teskey", "Blues soft, grain"],
          ["Loyle Carner / Froukje", "Poche plus urbaine / EU"],
        ]}
      />

      <Callout tone="warning" title="Méthode">
        Pas de librosa sur ces 270 titres (Spotify). L&apos;analyse = metadata
        playlist + heuristiques artistes/langue + recettes d&apos;accords
        typiques du catalogue.
      </Callout>
    </Stack>
  );
}

function BramCreation() {
  return (
    <Stack gap={18}>
      <Callout tone="success" title="Brief studio Bram — priorité #1">
        Pose une grille <Text weight="semibold">G–C–D–Em</Text> à{" "}
        <Text weight="semibold">88–94 BPM</Text>, guitare acoustique
        fingerstyle, voix soft EN, beaucoup d&apos;air. Si ça sonne « trop
        produit », enlève une couche.
      </Callout>

      <H2>3 lanes de création</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader trailing={<Text size="small">#1</Text>}>
            Island folk
          </CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">G – C – D – Em</Text>
              <Text size="small" tone="secondary">
                I–IV–V–vi · ~92 BPM · EN · steel/nylon
              </Text>
              <Text size="small">
                Capo optionnel. Percussion : shaker / body guitar. Zéro 808.
              </Text>
              <Text size="small" tone="secondary">
                Lyric : morning light / ocean / small joys
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Text size="small">#2</Text>}>
            Soft pop campfire
          </CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">C – G – Am – F</Text>
              <Text size="small" tone="secondary">
                I–V–vi–IV · ~88 BPM · Mayer / Bahamas
              </Text>
              <Text size="small">
                Couplet intimiste, refrain ouvert. Doubles voix très légères.
              </Text>
              <Text size="small" tone="secondary">
                Lyric : stay / kitchen talks / forgiveness
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Text size="small">#3</Text>}>
            Blues / soul soft
          </CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">Am – G – C – F</Text>
              <Text size="small" tone="secondary">
                ~78 BPM · EN · grain + harmonica optionnel
              </Text>
              <Text size="small">
                Moins beach, plus story. Laisser des mesures quasi vides.
              </Text>
              <Text size="small" tone="secondary">
                Lyric : worn roads / honest blame / quiet strength
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <H2>Checklist DAW Bram</H2>
      <Table
        striped
        headers={["Étape", "Action", "Critère OK"]}
        rows={[
          ["Tempo", "Click 90 BPM", "On peut marcher lentement dessus"],
          ["Guitare", "Voicing ouvert, fingerstyle", "Belle seule, sans beat"],
          ["Voix", "Proche micro, peu de reverb", "Intimité > polish"],
          ["Perc", "Shaker / brush only", "Pas de drop"],
          ["Paroles EN", "8–12 lignes concrètes", "Images du quotidien"],
          ["Espace", "Couper 1 élément", "Respiration audible"],
        ]}
      />

      <H2>Structure song</H2>
      <Table
        striped
        headers={["Section", "Barres", "Idée"]}
        rows={[
          ["Intro guitare", "4–8", "Motif fingerstyle seul"],
          ["Verse", "8–16", "Voix + guitare · presque dry"],
          ["Chorus", "8", "Ouvre la voix · +shaker"],
          ["Verse 2", "8", "Petite contre-ligne"],
          ["Bridge", "8", "Half-time ou Am color"],
          ["Final", "8–16", "Revenir nu ou +1 harmonie"],
        ]}
      />

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Prompts EN</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text size="small">« Bare feet on the kitchen floor… »</Text>
              <Text size="small">« We let the weekend take its time… »</Text>
              <Text size="small">« Salt on the window, soft radio… »</Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Lane bonus — alt soft</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text size="small">
                Si tu vises Loyle Carner / Froukje : même tempo lent, flow plus
                parlé, kick très soft, guitare en boucle courte.
              </Text>
              <Text size="small" tone="secondary">
                Toujours EN · densifier un peu sans quitter le Chill
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>
    </Stack>
  );
}

/* ===================== DUO ===================== */

function DuoSection() {
  const [tab, setTab] = useCanvasState<DuoTab>("duo-tab", "concepts");
  return (
    <Stack gap={16}>
      <Grid columns={COL_STATS} gap={12}>
        <Stat value="100–108" label="BPM pont" tone="info" />
        <Stat value="EN (+ FR)" label="Langue" />
        <Stat value="69%" label="Gaytitude duo" />
        <Stat value="Guit+pad" label="Timbre mix" />
      </Grid>
      <Callout tone="info" title="Objectif duo">
        Terrain commun = EN + émotion soft + 4 accords. Bram pose
        l&apos;ossature acoustique (~90) · Rafael apporte couleur prod et lift
        (~118) · rencontre à <Text weight="semibold">100–108 BPM</Text>. IG duo
        69% = sensitive-pop accessible, pas club.
      </Callout>

      <Row gap={8} wrap>
        <Pill active={tab === "overlap"} onClick={() => setTab("overlap")}>
          Analyse croisée
        </Pill>
        <Pill active={tab === "roles"} onClick={() => setTab("roles")}>
          Qui fait quoi
        </Pill>
        <Pill active={tab === "session"} onClick={() => setTab("session")}>
          Session
        </Pill>
        <Pill active={tab === "concepts"} onClick={() => setTab("concepts")}>
          Concepts
        </Pill>
      </Row>

      {tab === "overlap" && <DuoOverlap />}
      {tab === "roles" && <DuoRoles />}
      {tab === "session" && <DuoSession />}
      {tab === "concepts" && <DuoConcepts />}
    </Stack>
  );
}

function DuoOverlap() {
  return (
    <Stack gap={16}>
      <H2>Indice de Gaytitude — duo</H2>
      <GaytitudeBlock who="duo" />
      <BarChart
        categories={["Bram", "Duo", "Rafael"]}
        series={[{ name: "IG (%)", data: [57, 69, 81] }]}
        height={180}
      />
      <Text size="small" tone="secondary">
        Lecture : Rafael tire le duo vers le sensitive-pop ; Bram ramène vers le
        chill guitar soft. Ensemble = émotion accessible, pas club.
      </Text>

      <H2>Comparaison playlist → création</H2>
      <Table
        striped
        stickyHeader
        headers={["Axe", "Rafael", "Bram", "Pont duo"]}
        rows={[
          ["Source", "776 likes YT / 726 MP3", "270 Spotify Chill", "Goûts réels des deux"],
          ["Tempo", "~118 (100–140)", "~90 (80–100)", "100–108 BPM"],
          ["Langue", "EN + FR fort", "EN ~90%", "EN + pont FR optionnel"],
          ["Timbre", "voix + synth + piano", "guitare + voix soft", "guitare + pad"],
          ["Harmonie", "vi–IV–I–V (D#/E)", "I–IV–V–vi / campfire", "C–G–Am–F · Am–F–C–G"],
          ["Mood", "électro-mélancolie mid", "chill / island / blues", "mélancolie chaude"],
          ["Densité", "plus produite", "espace / room", "dry verse → wet chorus"],
          ["Risque", "trop EDM", "trop plat / demo", "garder les 2 tests"],
        ]}
      />

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Tempo — zone de rencontre</CardHeader>
          <CardBody>
            <BarChart
              categories={["Bram ~90", "Duo ~104", "Rafael ~118"]}
              series={[{ name: "BPM cible", data: [90, 104, 118] }]}
              height={180}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Grilles communes</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">C – G – Am – F</Text>
              <Text size="small" tone="secondary">
                Bram campfire · Rafael I–V–vi–IV classique
              </Text>
              <Text weight="semibold">Am – F – C – G</Text>
              <Text size="small" tone="secondary">
                Rafael vi–IV–I–V · Bram ballade mineure
              </Text>
              <Text weight="semibold">G – Em – C – D</Text>
              <Text size="small" tone="secondary">
                Bram island · Rafael arpèges synth sur Em/C
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="success" title="Style croisé qui résonne">
        Soft emotional pop acoustique + couche électro discrète — HAEVN meets
        Jack Johnson, ou Pomme + pad léger type Lost Frequencies.
      </Callout>
    </Stack>
  );
}

function DuoRoles() {
  return (
    <Stack gap={16}>
      <Table
        striped
        stickyHeader
        headers={["Domaine", "Bram mène", "Rafael mène", "Ensemble"]}
        rows={[
          ["Guitare / skeleton", "Oui", "Doubles / soutien", "Grille fixée à 2"],
          ["Beat / groove", "Shaker, brush", "Kick/clap électro", "Layer progressif"],
          ["Synth / pads", "Rare", "Oui — atmosphère", "Entre au 2e couplet"],
          ["Voix lead", "Soft / grain", "Pop / stacks", "Duo refrain"],
          ["Paroles EN", "Oui", "Oui", "Co-write"],
          ["Paroles FR", "Support", "Oui (pont)", "4–8 barres max v1"],
          ["Structure", "Forme A–B acoustique", "Lift chorus", "A–A–B + lift"],
          ["Mix", "Room, dry", "Width, FX", "Dry→wet"],
        ]}
      />

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Leadership Bram</CardHeader>
          <CardBody>
            <Text size="small">
              Island folk, blues soft, tempo lent, guitare, silence, lyrics EN
              du quotidien, groove « body ».
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Leadership Rafael</CardHeader>
          <CardBody>
            <Text size="small">
              Couleur 4 chords pop, synth/piano, arrangement, énergie mid,
              option FR, finish streaming.
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <H3>Pièges duo</H3>
      <Table
        headers={["Piège", "Fix"]}
        rows={[
          ["128 BPM EDM d’emblée", "Cap ~110 sur la v1"],
          ["Trop de couches au départ", "Guitare + voix d’abord 20 min"],
          ["Grille chromatique complexe", "Max 4 accords diatoniques"],
          ["FR sur tout le titre", "FR = pont / ad-lib seulement"],
        ]}
      />
    </Stack>
  );
}

function DuoSession() {
  return (
    <Stack gap={16}>
      <H2>Session type — 90 minutes</H2>
      <Table
        striped
        headers={["Min", "Action", "Qui", "Livrable"]}
        rows={[
          ["0–10", "Choisir grille + BPM 104", "2", "C–G–Am–F noté"],
          ["10–25", "Guitare + click + groove", "Bram", "Boucle 8 barres"],
          ["25–40", "Hum mélodie EN", "2", "2 motifs (V/C)"],
          ["40–55", "Pad + kick soft + delay", "Rafael", "Lift audible"],
          ["55–70", "Paroles EN + test FR pont", "2", "8+4 lignes"],
          ["70–85", "Arrange verse dry / chorus wet", "Rafael", "Diff sections"],
          ["85–90", "Export rough + notes", "2", "WAV + grille/BPM"],
        ]}
      />
      <Callout tone="success" title="Double test de réussite">
        1) Sans synth, la chanson tient (Bram). 2) Sans guitare, émotion/prod
        tient (Rafael). Les deux doivent passer avant de figer.
      </Callout>
    </Stack>
  );
}

function DuoConcepts() {
  return (
    <Stack gap={16}>
      <H2>Concepts prêts à composer</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>1 — Late light</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text weight="semibold">C–G–Am–F · 104 BPM · EN</Text>
              <Text size="small">
                Bram : fingerstyle C. Rafael : pad + clap 2/4. Refrain duo.
              </Text>
              <Text size="small" tone="secondary">
                Lyric seed : « leave the porch light on for me… »
              </Text>
              <Text size="small">Forme : Intro Guit → V → C → V → C → Bridge → C</Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>2 — Warm minor</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text weight="semibold">Am–F–C–G · 100 BPM · EN + FR pont</Text>
              <Text size="small">
                Plus « Rafael émotion ». Bram pose Am fingerstyle. Pont FR 4–8
                barres.
              </Text>
              <Text size="small" tone="secondary">
                Lyric seed : « we talk in circles around the quiet… »
              </Text>
              <Text size="small">Strip au bridge puis retour chorus plein</Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>3 — Island lift</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text weight="semibold">G–Em–C–D · 108 BPM · EN</Text>
              <Text size="small">
                Bram island groove. Rafael arpège synth sur Em/C + shaker.
              </Text>
              <Text size="small" tone="secondary">
                Lyric seed : « salt on the window, soft radio… »
              </Text>
              <Text size="small">Le plus « summer » des trois</Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Divider />

      <H3>Recette d&apos;écriture à deux (une page)</H3>
      <Table
        striped
        headers={["Bloc", "Contenu", "Owner"]}
        rows={[
          ["Titre de travail", "3 mots max", "2"],
          ["Promesse émotionnelle", "1 phrase", "2"],
          ["Grille + BPM + key", "ex. C · 104 · C major", "2"],
          ["Hook 1 ligne", "EN", "Qui a l’idée"],
          ["Couplet images", "4 lignes concrètes", "Bram draft"],
          ["Refrain abstract", "4 lignes émotion", "Rafael draft"],
          ["Pont", "EN ou FR", "Rafael si FR"],
        ]}
      />
    </Stack>
  );
}
