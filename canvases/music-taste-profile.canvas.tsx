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
type RafaelTab = "brief" | "harmonies" | "tempo" | "mood";
type BramTab = "brief" | "style" | "recettes";
type DuoTab = "overlap" | "roles" | "session";

const COL = "repeat(auto-fit, minmax(min(100%, 260px), 1fr))";
const COL_STATS = "repeat(auto-fit, minmax(min(100%, 140px), 1fr))";

export default function MusicTasteProfile() {
  const [person, setPerson] = useCanvasState<Person>("person", "rafael");

  return (
    <Stack gap={18}>
      <Stack gap={6}>
        <H1>Création — Rafael × Bram</H1>
        <Text tone="secondary">
          Profils séparés + brief à deux · instruments · langue · rythme ·
          suites d&apos;accords · qui fait quoi
        </Text>
      </Stack>

      <Row gap={8} wrap>
        <Pill active={person === "rafael"} onClick={() => setPerson("rafael")}>
          Rafael (YouTube)
        </Pill>
        <Pill active={person === "bram"} onClick={() => setPerson("bram")}>
          Bram (Spotify Chill)
        </Pill>
        <Pill active={person === "duo"} onClick={() => setPerson("duo")}>
          À deux
        </Pill>
      </Row>

      {person === "rafael" && <RafaelSection />}
      {person === "bram" && <BramSection />}
      {person === "duo" && <DuoSection />}

      <Text size="small" tone="secondary">
        Rafael : librosa sur MP3 likes YT · Bram : Spotify Chill (270 titres) +
        recettes curatorielles · valide à l&apos;oreille / DAW
      </Text>
    </Stack>
  );
}

/* ===================== RAFAEL ===================== */

function RafaelSection() {
  const [tab, setTab] = useCanvasState<RafaelTab>("rafael-tab", "brief");
  return (
    <Stack gap={16}>
      <Grid columns={COL_STATS} gap={12}>
        <Stat value="Cm–G#–D#–A#" label="Grille #1" tone="info" />
        <Stat value="~118 BPM" label="Tempo" />
        <Stat value="EN (+ FR)" label="Langue" />
        <Stat value="Voix + synth" label="Timbre" />
      </Grid>

      <Row gap={8} wrap>
        <Pill active={tab === "brief"} onClick={() => setTab("brief")}>
          Brief
        </Pill>
        <Pill active={tab === "harmonies"} onClick={() => setTab("harmonies")}>
          Harmonies
        </Pill>
        <Pill active={tab === "tempo"} onClick={() => setTab("tempo")}>
          Tempo & langue
        </Pill>
        <Pill active={tab === "mood"} onClick={() => setTab("mood")}>
          Mood
        </Pill>
      </Row>

      {tab === "brief" && <RafaelBrief />}
      {tab === "harmonies" && <RafaelHarmonies />}
      {tab === "tempo" && <RafaelTempo />}
      {tab === "mood" && <RafaelMood />}
    </Stack>
  );
}

function RafaelBrief() {
  return (
    <Stack gap={16}>
      <Callout tone="info" title="Brief Rafael">
        Boucle 4 accords zone D# (vi–IV–I–V), ~118 BPM, lead vocal EN, prod
        voix + synth. Couleur mineure (~58%). Alternative : G–D–A–Bm ~112 BPM.
      </Callout>
      <H2>3 lanes</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>A — Pop mineure brillante</CardHeader>
          <CardBody>
            <Text weight="semibold">Cm – G# – D# – A#</Text>
            <Text size="small" tone="secondary">
              ~118 BPM · EN · D# · rotations du même cycle
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>B — Pop / folk D</CardHeader>
          <CardBody>
            <Text weight="semibold">G – D – A – Bm</Text>
            <Text size="small" tone="secondary">
              ~112 BPM · EN · D major · anthem midtempo
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>C — Électro uplift</CardHeader>
          <CardBody>
            <Text weight="semibold">C#m – A – E – B</Text>
            <Text size="small" tone="secondary">
              ~121 BPM · groove 120–140 · Walker territory
            </Text>
          </CardBody>
        </Card>
      </Grid>
      <Table
        striped
        headers={["Étape", "Cible"]}
        rows={[
          ["Tempo", "116–120 BPM"],
          ["Grille", "Cm–G#–D#–A# (8–16 barres)"],
          ["Lead", "Voix + synth support"],
          ["Langue", "EN d’abord · FR variante"],
        ]}
      />
    </Stack>
  );
}

function RafaelHarmonies() {
  return (
    <Stack gap={16}>
      <Table
        striped
        stickyHeader
        headers={["Suite", "°", "BPM", "Lang", "Vu"]}
        rows={[
          ["Cm-G#-D#-A#", "vi-IV-I-V", "118", "en", "21"],
          ["G#-D#-A#-Cm", "vi-IV-I-V", "118", "en", "19"],
          ["G-D-A-Bm", "IV-I-V-vi", "112", "en", "18"],
          ["D-A-Bm-G", "IV-I-V-vi", "112", "en", "17"],
          ["C#m-A-E-B", "vi-IV-I-V", "121", "en", "15"],
        ]}
      />
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Degrés (617 pistes)</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={["vi-IV-I-V", "IV-I-V-vi", "I-V-vi-IV", "V-vi-IV-I"]}
              series={[{ name: "Occurrences", data: [102, 90, 76, 69] }]}
              height={200}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Suites top</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={["Cm-G#-D#-A#", "G#-D#-A#-Cm", "G-D-A-Bm", "D-A-Bm-G"]}
              series={[{ name: "Occurrences", data: [21, 19, 18, 17] }]}
              height={200}
            />
          </CardBody>
        </Card>
      </Grid>
    </Stack>
  );
}

function RafaelTempo() {
  return (
    <Stack gap={16}>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>BPM</CardHeader>
          <CardBody>
            <BarChart
              categories={["<80", "80–100", "100–120", "120–140", "140+"]}
              series={[{ name: "Pistes", data: [54, 145, 126, 175, 117] }]}
              height={200}
            />
            <Text size="small" tone="secondary">
              Médiane 117.5
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Langues</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={["en", "inconnu", "fr", "instrumental"]}
              series={[{ name: "Pistes", data: [330, 160, 81, 41] }]}
              height={200}
            />
          </CardBody>
        </Card>
      </Grid>
    </Stack>
  );
}

function RafaelMood() {
  return (
    <Stack gap={16}>
      <Grid columns={COL_STATS} gap={12}>
        <Stat value="58%" label="Mineur" tone="info" />
        <Stat value="voix" label="Instrument #1" />
        <Stat value="synth" label="Instrument #2" />
        <Stat value="piano" label="Instrument #3" />
      </Grid>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Mode</CardHeader>
          <CardBody>
            <PieChart
              data={[
                { label: "Mineur", value: 423 },
                { label: "Majeur", value: 303 },
              ]}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Clusters</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={["midtempo", "uplift", "électro-mélan.", "intime"]}
              series={[{ name: "Part %", data: [32, 24, 24, 20] }]}
              height={180}
            />
          </CardBody>
        </Card>
      </Grid>
    </Stack>
  );
}

/* ===================== BRAM ===================== */

function BramSection() {
  const [tab, setTab] = useCanvasState<BramTab>("bram-tab", "brief");
  return (
    <Stack gap={16}>
      <Grid columns={COL_STATS} gap={12}>
        <Stat value="G–C–D–Em" label="Grille #1" tone="info" />
        <Stat value="~90 BPM" label="Tempo" />
        <Stat value="EN ~90%" label="Langue" />
        <Stat value="Guitare" label="Timbre" />
      </Grid>

      <Callout tone="info" title="Playlist Chill — Bram van Beurden">
        270 titres Spotify · cœur Jack Johnson / Bobby Alu / Bahamas /
        Frankenreiter / Mayer + poche alt soft (Loyle Carner, Froukje, Fike).
        Source :{" "}
        <Text weight="semibold">open.spotify.com/playlist/7prdtzDctYFscp8PgFsp6i</Text>
      </Callout>

      <Row gap={8} wrap>
        <Pill active={tab === "brief"} onClick={() => setTab("brief")}>
          Brief création
        </Pill>
        <Pill active={tab === "style"} onClick={() => setTab("style")}>
          Style & artistes
        </Pill>
        <Pill active={tab === "recettes"} onClick={() => setTab("recettes")}>
          Recettes
        </Pill>
      </Row>

      {tab === "brief" && <BramBrief />}
      {tab === "style" && <BramStyle />}
      {tab === "recettes" && <BramRecettes />}
    </Stack>
  );
}

function BramBrief() {
  return (
    <Stack gap={16}>
      <Callout tone="success" title="Ce que Bram écrit en premier">
        Une grille campfire en G ou C, ~85–95 BPM, guitare acoustique
        fingerstyle, voix soft EN, espace et silence — pas de drop EDM.
      </Callout>

      <H2>3 lanes Bram</H2>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>A — Island folk</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text weight="semibold">G – C – D – Em</Text>
              <Text size="small" tone="secondary">
                I–IV–V–vi · ~92 BPM · EN · guitare steel / nylon
              </Text>
              <Text size="small">
                ADN Jack Johnson / Frankenreiter / Bobby Alu. Groove léger,
                shaker, pas de 808.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>B — Soft pop campfire</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text weight="semibold">C – G – Am – F</Text>
              <Text size="small" tone="secondary">
                I–V–vi–IV · ~88 BPM · EN · Mayer / Bahamas
              </Text>
              <Text size="small">
                Plus « chanson » : couplet intimiste, refrain ouvert.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>C — Blues / soul soft</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text weight="semibold">Am – G – C – F</Text>
              <Text size="small" tone="secondary">
                ~78 BPM · EN · Keb&apos; Mo&apos; / Kiwanuka / Stapleton
              </Text>
              <Text size="small">
                Plus de grain vocal, harmonica optionnel, moins « beach ».
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <H3>Checklist DAW Bram</H3>
      <Table
        striped
        headers={["Étape", "Cible", "Pourquoi"]}
        rows={[
          ["Tempo", "85–95 BPM", "Chill dominant · pas 120+"],
          ["Grille", "G–C–D–Em ou C–G–Am–F", "Cœur island / campfire"],
          ["Instrument", "Guitare acoustique lead", "Timbre #1 de la playlist"],
          ["Voix", "Soft, proche micro", "Presque tout est chanté"],
          ["Langue", "EN", "~90% des titres"],
          ["Prod", "Peu d’éléments, room mic", "Respiration > densité"],
        ]}
      />
    </Stack>
  );
}

function BramStyle() {
  return (
    <Stack gap={16}>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Artistes récurrents</CardHeader>
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
                "Froukje",
                "Dominic Fike",
                "Keb' Mo'",
              ]}
              series={[{ name: "Titres", data: [12, 5, 4, 3, 3, 3, 3, 3, 3, 2] }]}
              height={280}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Poches de style</CardHeader>
          <CardBody>
            <BarChart
              horizontal
              categories={[
                "acoustic island",
                "chill / soft alt",
                "hip-hop soft",
                "world / afro",
                "blues / soul",
              ]}
              series={[{ name: "Signal", data: [34, 120, 15, 12, 12] }]}
              height={220}
            />
            <Text size="small" tone="secondary">
              Heuristique artistes — pas audio tagging
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
              Anglais dominant · poche NL/DE/world
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

      <Table
        striped
        headers={["Référence", "Pourquoi l’écouter"]}
        rows={[
          ["Jack Johnson — Banana Pancakes", "Tempo + fingerstyle + EN soft"],
          ["Donavon Frankenreiter — Big Wave", "Groove island, guitare ouverte"],
          ["John Mayer — Slow Dancing…", "Ballade émotionnelle, C/G family"],
          ["Keb' Mo' / Teskey", "Blues soft, grain vocal"],
          ["Loyle Carner / Froukje", "Poche plus contemporaine / spoken"],
        ]}
      />
    </Stack>
  );
}

function BramRecettes() {
  return (
    <Stack gap={16}>
      <H2>Recettes suite × tempo × langue × instrument</H2>
      <Table
        striped
        stickyHeader
        headers={["Suite", "°", "BPM", "Lang", "Instrument", "Usage"]}
        rows={[
          ["G–C–D–Em", "I-IV-V-vi", "92", "en", "guitare FS", "Lane A island"],
          ["C–G–Am–F", "I-V-vi-IV", "88", "en", "guitare + voix", "Lane B campfire"],
          ["Am–G–C–F", "vi-V-I-IV", "78", "en", "guitare + harp", "Lane C blues"],
          ["Dm–Bb–F–C", "i-bVI-…", "96", "es", "guitare + perc", "World / latin"],
        ]}
      />
      <Callout tone="warning" title="Limite méthode">
        Pas d&apos;analyse chroma piste-par-piste ici (Spotify, pas MP3). Les
        grilles sont typiques du catalogue Chill de Bram — à valider à
        l&apos;oreille.
      </Callout>
    </Stack>
  );
}

/* ===================== DUO ===================== */

function DuoSection() {
  const [tab, setTab] = useCanvasState<DuoTab>("duo-tab", "overlap");
  return (
    <Stack gap={16}>
      <Callout tone="info" title="Objectif duo">
        Trouver le terrain commun (langue EN, émotion soft, grilles 4 accords)
        puis se répartir : Bram = ossature acoustique / groove lent · Rafael =
        couleur prod, synth, arrangement, option FR.
      </Callout>

      <Row gap={8} wrap>
        <Pill active={tab === "overlap"} onClick={() => setTab("overlap")}>
          Terrain commun
        </Pill>
        <Pill active={tab === "roles"} onClick={() => setTab("roles")}>
          Qui fait quoi
        </Pill>
        <Pill active={tab === "session"} onClick={() => setTab("session")}>
          Session type
        </Pill>
      </Row>

      {tab === "overlap" && <DuoOverlap />}
      {tab === "roles" && <DuoRoles />}
      {tab === "session" && <DuoSession />}
    </Stack>
  );
}

function DuoOverlap() {
  return (
    <Stack gap={16}>
      <H2>Comparaison rapide</H2>
      <Table
        striped
        headers={["Axe", "Rafael", "Bram", "Pont duo"]}
        rows={[
          ["Tempo", "~118 (100–140)", "~90 (80–100)", "100–108 BPM"],
          ["Langue", "EN + FR fort", "EN ~90%", "EN (FR en bridge/outro)"],
          ["Instrument", "voix + synth + piano", "guitare + voix soft", "guitare + pad synth"],
          ["Harmonie", "vi–IV–I–V (D#/E)", "I–IV–V–vi / I–V–vi–IV", "C–G–Am–F ou Am–F–C–G"],
          ["Mood", "électro-mélancolie", "chill / island / blues", "mélancolie chaude, mid"],
          ["Densité", "prod plus dense", "espace / room", "couple acoustique → build léger"],
        ]}
      />

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Grilles qui marchent pour les deux</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text weight="semibold">1. C – G – Am – F</Text>
              <Text size="small" tone="secondary">
                Bram : campfire · Rafael : pop classique (I–V–vi–IV)
              </Text>
              <Text weight="semibold">2. Am – F – C – G</Text>
              <Text size="small" tone="secondary">
                Rafael : vi–IV–I–V · Bram : ballade mineure soft
              </Text>
              <Text weight="semibold">3. G – Em – C – D</Text>
              <Text size="small" tone="secondary">
                Bram island · Rafael peut ajouter arps synth sur Em/C
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Tempo & langue — zone de rencontre</CardHeader>
          <CardBody>
            <BarChart
              categories={["Bram ~90", "Duo ~104", "Rafael ~118"]}
              series={[{ name: "BPM cible", data: [90, 104, 118] }]}
              height={180}
            />
            <Text size="small" tone="secondary">
              Langue : EN sur couplet/refrain · FR option Rafael sur pont
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="success" title="Style « qui résonne »">
        Soft emotional pop acoustique avec une couche électro discrète —
        pense HAEVN meets Jack Johnson, ou Pomme + pad Lost Frequencies léger.
      </Callout>
    </Stack>
  );
}

function DuoRoles() {
  return (
    <Stack gap={16}>
      <H2>Qui fait quoi</H2>
      <Table
        striped
        stickyHeader
        headers={["Domaine", "Bram mène", "Rafael mène", "Ensemble"]}
        rowTone={["info", "info", undefined, "info", undefined, undefined, "info"]}
        rows={[
          ["Guitare / skeleton", "Oui — fingerstyle, voicings", "Soutien / doubles", "Grille fixée à 2"],
          ["Beat / groove", "Shaker, brush, kick soft", "Kick/clap/électro mid", "Layer progressif"],
          ["Synth / pads", "Non (ou très rare)", "Oui — atmosphère", "Introduire au 2e couplet"],
          ["Voix lead", "Timbre soft / grain", "Timbre pop / stacked", "Duo refrain / call-response"],
          ["Paroles EN", "Naturel Chill", "Naturel likes YT", "Co-write couplet"],
          ["Paroles FR", "Support", "Oui — variante", "Pont FR optionnel"],
          ["Structure song", "Forme acoustique A–B", "Drop / lift chorus", "A–A–B–A + lift léger"],
          ["Mix mood", "Room, dry vocals", "Width, FX, delay", "Dry verse → wet chorus"],
        ]}
      />

      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Bram — zones de leadership</CardHeader>
          <CardBody>
            <Text size="small">
              Island folk, blues soft, tempo lent, guitare, silence, lyrics EN
              intimistes, groove « body » (pas club).
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Rafael — zones de leadership</CardHeader>
          <CardBody>
            <Text size="small">
              Couleur harmonique pop 4 chords, synth/piano, arrangement,
              énergie mid/up, option FR, finish radio / streaming.
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <H3>Pièges à éviter</H3>
      <Table
        headers={["Piège", "Pourquoi", "Fix"]}
        rows={[
          ["Partir à 128 BPM EDM", "Sort du centre Bram", "Cap à ~110 sur v1"],
          ["Trop de couches d’emblée", "Tue le Chill", "Guitare+voix d’abord"],
          ["Grille trop chromatique", "Bram = diatonique simple", "Max 4 accords"],
          ["FR partout", "Bram = EN dominant", "FR = pont / ad-lib"],
        ]}
      />
    </Stack>
  );
}

function DuoSession() {
  return (
    <Stack gap={16}>
      <H2>Session type (90 min)</H2>
      <Table
        striped
        headers={["Min", "Action", "Qui"]}
        rows={[
          ["0–10", "Choisir grille commune : C–G–Am–F · capot éventuel", "Les deux"],
          ["10–25", "Bram pose guitare + groove 100–106 BPM (click)", "Bram"],
          ["25–40", "Mélodie lead EN sur 8 barres (hum d’abord)", "Les deux"],
          ["40–55", "Rafael ajoute pad + kick soft + delay voix", "Rafael"],
          ["55–70", "Écrire couplet EN · tester 4 lignes FR en pont", "Les deux"],
          ["70–85", "Arrangement : verse dry → chorus +1 couche", "Rafael"],
          ["85–90", "Exporter rough + noter grille/BPM/tonalité", "Les deux"],
        ]}
      />

      <Divider />

      <H3>3 concepts prêts à composer</H3>
      <Grid columns={COL} gap={12}>
        <Card>
          <CardHeader>Concept 1 — Late light</CardHeader>
          <CardBody>
            <Stack gap={4}>
              <Text size="small">C–G–Am–F · 104 BPM · EN</Text>
              <Text size="small" tone="secondary">
                Bram guitare · Rafael pad + clap léger · refrain duo
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Concept 2 — Warm minor</CardHeader>
          <CardBody>
            <Stack gap={4}>
              <Text size="small">Am–F–C–G · 100 BPM · EN (+ FR pont)</Text>
              <Text size="small" tone="secondary">
                Plus « Rafael émotion » · Bram fingerstyle Am
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Concept 3 — Island lift</CardHeader>
          <CardBody>
            <Stack gap={4}>
              <Text size="small">G–Em–C–D · 108 BPM · EN</Text>
              <Text size="small" tone="secondary">
                Bram island groove · Rafael arpège synth sur Em/C
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="success" title="Critère de réussite">
        Si on enlève le synth, la chanson tient encore (test Bram). Si on enlève
        la guitare, l&apos;émotion/prod tient encore (test Rafael). Les deux
        tests doivent passer.
      </Callout>
    </Stack>
  );
}
