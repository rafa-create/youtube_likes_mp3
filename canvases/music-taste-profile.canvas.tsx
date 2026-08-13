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
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

export default function MusicTasteProfile() {
  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Profil musical — likes YouTube</H1>
        <Text tone="secondary">
          776 likes / 726 MP3 · librosa sur 80 pistes (90 s) · tonalité =
          corrélation chroma (Krumhansl-Schmuckler)
        </Text>
      </Stack>

      <Grid columns={4} gap={16}>
        <Stat value="776" label="Vidéos aimées" />
        <Stat value="726" label="MP3 locaux" />
        <Stat value="118" label="BPM médian" />
        <Stat value="51%" label="Mode mineur" tone="info" />
      </Grid>

      <Callout tone="info" title="Verdict rapide">
        Équilibre majeur/mineur, tempo pop ~110–130 BPM, centres tonals G / C /
        A (+ C# mineur). Mélancolie danceable + piano néo-classique + pop FR
        (Pomme, Sia, Alan Walker, HAEVN).
      </Callout>

      <Grid columns={2} gap={20}>
        <Card>
          <CardHeader>Mode (échantillon audio)</CardHeader>
          <CardBody>
            <PieChart
              data={[
                { label: "Mineur", value: 41 },
                { label: "Majeur", value: 39 },
              ]}
            />
            <Text size="small" tone="secondary">
              41 mineur / 39 majeur sur 80 pistes
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Répartition BPM</CardHeader>
          <CardBody>
            <BarChart
              categories={["<70", "70–90", "90–110", "110–130", "130–150", "150+"]}
              series={[
                {
                  name: "Nombre de pistes",
                  data: [2, 11, 16, 33, 7, 11],
                },
              ]}
              height={220}
            />
            <Text size="small" tone="secondary">
              Médiane 117.5 · P25–P75 : 99–129 BPM
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Card>
        <CardHeader>Tonalités les plus fréquentes</CardHeader>
        <CardBody>
          <BarChart
            horizontal
            categories={[
              "G minor",
              "C# minor",
              "C major",
              "G major",
              "A major",
              "D# major",
              "B minor",
              "G# minor",
            ]}
            series={[
              {
                name: "Occurrences (échantillon)",
                data: [7, 7, 6, 6, 5, 4, 4, 4],
              },
            ]}
            height={260}
          />
          <Text size="small" tone="secondary">
            Estimation chroma — tendances, pas un lead sheet exact
          </Text>
        </CardBody>
      </Card>

      <Grid columns={2} gap={20}>
        <Card>
          <CardHeader>Artistes récurrents (titres playlist)</CardHeader>
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
                "Tom Odell",
                "Tony Ann",
              ]}
              series={[
                {
                  name: "Mentions",
                  data: [15, 13, 7, 7, 7, 6, 5, 5, 4, 4],
                },
              ]}
              height={280}
            />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Signaux de style (mots-clés titres)</CardHeader>
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
              series={[
                {
                  name: "Hits heuristiques",
                  data: [45, 44, 43, 33, 29, 21, 14],
                },
              ]}
              height={280}
            />
          </CardBody>
        </Card>
      </Grid>

      <Divider />

      <Stack gap={12}>
        <H2>Patterns harmoniques utiles</H2>
        <Grid columns={3} gap={12}>
          <Card>
            <CardHeader>Familles d’accords</CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Text weight="semibold">G / Em / C / D</Text>
                <Text size="small" tone="secondary">
                  Zone G majeur / E mineur — pop / folk
                </Text>
                <Text weight="semibold">A / F#m / D / E</Text>
                <Text size="small" tone="secondary">
                  Centre A — ballades / midtempo
                </Text>
                <Text weight="semibold">C#m / E / B / A</Text>
                <Text size="small" tone="secondary">
                  Couleur électro / triste brillante
                </Text>
              </Stack>
            </CardBody>
          </Card>
          <Card>
            <CardHeader>Progressions typiques</CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Text>
                  Tu as liké « Axis of Awesome — 4 Four Chord Song » : la grille{" "}
                  <Text weight="semibold">I–V–vi–IV</Text> est dans ton ADN
                  d’écoute.
                </Text>
                <Text size="small" tone="secondary">
                  Autres candidats : vi–IV–I–V, i–VI–III–VII (pop mineure).
                </Text>
              </Stack>
            </CardBody>
          </Card>
          <Card>
            <CardHeader>Mood composite</CardHeader>
            <CardBody>
              <Stack gap={8}>
                <H3>Électro-mélancolie + piano</H3>
                <Text size="small">
                  Walker / Lost Frequencies / Nightcore d’un côté ; piano
                  (Tony Ann, Einaudi…) et Pomme & Sia au milieu.
                </Text>
                <Text size="small" tone="secondary">
                  Tempo confort ~118 BPM : danceable sans hard EDM.
                </Text>
              </Stack>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      <Callout tone="warning" title="Pour des grilles accords exactes">
        Outils spécialisés : Chordify (accords piste par piste), Mixed In Key
        (DJ / tonalité), Cyanite.ai (analyse / similarité pro). Librosa reste
        une estimation globale.
      </Callout>

      <Stack gap={8}>
        <H2>Exemples du sample audio</H2>
        <Table
          headers={["Piste", "Tonalité estimée", "BPM"]}
          rows={[
            ["Pomme — Umbrella (acoustique)", "C major", "99"],
            ["[Ghost] Riders in the Sky", "A# minor", "108"],
            ["Alan Walker — Faded", "F# major*", "89"],
            ["AURORA — Running With The Wolves", "A minor", "83"],
            ["Alec Benjamin — Devil Doesn't Bargain", "D# major", "123"],
            ["Axis of Awesome — 4 Chord Song", "E major", "123"],
            ["Ben Cocks — So Cold", "A# major", "76"],
            ["André Rieu — The Lonely Shepherd", "D minor", "123"],
          ]}
        />
        <Text size="small" tone="secondary">
          *Estimation chroma parfois ambiguë (relatif majeur/mineur). Détail :
          music_profile.json
        </Text>
      </Stack>
    </Stack>
  );
}
