import { scenarioParagraph as source } from "../../game/scenarioDocument";
import { parcelNames, recipientNames } from "../names";
import type { SceneContext, SceneDefinition, SceneOption } from "../types";
import { LastmileArt } from "./LastmileArt";

export function lastmileOptions({ recipient }: SceneContext): SceneOption[] {
 const remote = recipient !== "arseniy";
 return [
  { id: "helicopter", label: source("2D9B5DEE"),
    result: [source("11ADFA69-text"), ...(remote ? [source("056B051D").replace("чума/ мест, где обитает Хабт", recipient === "alva" ? "чума" : "мест, где обитает Хабт")] : [])],
    score: {energy:-4, empathy:remote ? -2 : 0, efficiency:4},
    sourceIds:["2D9B5DEE", "11ADFA69-text", ...(remote ? ["056B051D"] : []), "22D5F7AA"] },
  { id:"rover", label:source("42123CE2"), result:[source("06D090A1-text")],
    score:{energy:4,empathy:3,efficiency:5}, sourceIds:["42123CE2","06D090A1-text","333D692C"] },
  { id:"robot", label:source("3B981493"), result:[source("5629AB4A"),source("2289FF3B")],
    score:{energy:-4,empathy:3,efficiency:-5}, sourceIds:["3B981493","5629AB4A","2289FF3B","67543BB5"] },
  { id:"pipe-carrier", label:source("4172314D"), result:[source("4E705130"),source("7F6FF7ED")],
    score:{energy:-5,empathy:0,efficiency:-3}, sourceIds:["4172314D","4E705130","7F6FF7ED","3052219F"] },
 ];
}
export const lastmileScene: SceneDefinition = {
 id:"lastmile", number:5, title:"Последние препятствия",
 product:"технологичные транспортные средства, которые использует «Снабжение»",
 intro:({recipient,parcel})=>[
  source("6B6E0ADA").replace("(имя персонажа)",recipientNames[recipient].dative),
  source("4A484891"),source("5214BC84"),
  source("51C60484").replace("(название подарка)",parcelNames[parcel].genitive).replace("(имени персонажа)",recipientNames[recipient].dative),
 ], options:lastmileOptions, Art:LastmileArt,
};
