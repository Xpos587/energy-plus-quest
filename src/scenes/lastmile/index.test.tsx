import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { parcelNames, recipientNames } from "../names";
import { source } from "../source";
import type { SceneContext } from "../types";
import { lastmileScene } from "./index";

const recipients = ["alva", "khor", "arseniy"] as const;
const parcels = ["camera", "socks", "boat"] as const;
describe("lastmileScene", () => {
  for (const recipient of recipients)
    for (const parcel of parcels) {
      const context: SceneContext = { recipient, parcel, profile: "student" };
      it(`${recipient}/${parcel}: exact copy, scores, provenance and illustrated outcomes`, () => {
        expect(lastmileScene.intro(context)).toEqual([
          source("p549").replace(
            "(имя персонажа)",
            recipientNames[recipient].dative,
          ),
          source("p551"),
          source("p552"),
          source("p554")
            .replace("(название подарка)", parcelNames[parcel].genitive)
            .replace("(имени персонажа)", recipientNames[recipient].dative),
        ]);
        const options = lastmileScene.options(context);
        expect(options.map((o) => o.id)).toEqual([
          "helicopter",
          "rover",
          "robot",
          "pipe-carrier",
        ]);
        expect(options.map((o) => o.label)).toEqual(
          ["p556", "p565", "p572", "p580"].map(source),
        );
        expect(options.map((o) => o.score)).toEqual([
          {
            energy: -4,
            empathy: recipient === "arseniy" ? 0 : -2,
            efficiency: 4,
          },
          { energy: 4, empathy: 3, efficiency: 5 },
          { energy: -4, empathy: 3, efficiency: -5 },
          { energy: -5, empathy: 0, efficiency: -3 },
        ]);
        expect(options[0].result).toEqual([
          source("p558"),
          ...(recipient === "arseniy"
            ? []
            : [
                source("p560").replace(
                  "чума/ мест, где обитает Хор",
                  recipient === "alva" ? "чума" : "мест, где обитает Хор",
                ),
              ]),
        ]);
        expect(options[1].result).toEqual([source("p567")]);
        expect(options[2].result).toEqual([source("p574"), source("p576")]);
        expect(options[3].result).toEqual([
          source("p582"),
          source("p584"),
          source("p585").replace(
            "беспилотник (для подарка «лодка» – снегоболотоход)",
            parcel === "boat" ? "снегоболотоход" : "беспилотник",
          ),
        ]);
        const provenance = [
          [
            "p556",
            "p558",
            ...(recipient === "arseniy" ? [] : ["p560"]),
            "p563",
          ],
          ["p565", "p567", "p569"],
          ["p572", "p574", "p576", "p578"],
          ["p580", "p582", "p584", "p585", "p587"],
        ];
        options.forEach((option, index) => {
          expect(option.sourceIds).toEqual(provenance[index]);
          const markup = renderToStaticMarkup(
            <lastmileScene.Art
              context={context}
              selectedId={option.id}
              showResult
            />,
          );
          expect(markup).toContain(`data-outcome="${option.id}"`);
          expect(markup).not.toContain("data-world-annotation");
          expect(markup).toContain(`data-event="${option.id}"`);
          expect(markup).toContain(`data-recipient="${recipient}"`);
          expect(markup).toContain("/scene-art/lastmile.png");
          expect(markup).toContain("<img");
          expect(markup).not.toContain("(для подарка");
          if (option.id === "pipe-carrier")
            expect(markup).toContain(
              `data-rescue="${parcel === "boat" ? "rover" : "drone"}"`,
            );
        });
        const markup = renderToStaticMarkup(
          <lastmileScene.Art
            context={context}
            showResult={false}
            onSelect={() => {}}
          />,
        );
        expect(markup).not.toContain("<button");
        expect(markup).not.toContain("data-event");
      });
    }
});
