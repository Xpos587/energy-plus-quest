import type { ParcelId } from "../../game/types";
import styles from "./RouteCompare.module.css";

/** Metres from each spot to the dispatch door, measured along the floor routes in
 *  design/scene-03/blender-v1/warehouse.py (ROUTE_M; checked by RouteCompare.test). */
export const routeMetres = { entrance: 56, camera: 29, socks: 36, boat: 44, hot: 21 } as const;

type Spot = "entrance" | "alphabet" | "keeper" | "wms";
export const routeRows = (parcel: ParcelId): { id: Spot; name: string; metres: number; who: string; ok: boolean }[] => [
  { id: "entrance", name: "У приёмки", metres: routeMetres.entrance, who: "Все, но далеко", ok: false },
  { id: "alphabet", name: "По алфавиту", metres: routeMetres[parcel], who: "Все, по букве", ok: false },
  { id: "keeper", name: "Кладовщик", metres: routeMetres.hot, who: "Только кладовщик", ok: false },
  { id: "wms", name: "Автоподбор", metres: routeMetres.hot, who: "Вся смена, в системе", ok: true },
];

/** After the choice: every spot side by side — how far the gift travels to dispatch
 *  and who can find it — so the player sees why one option beats the rest. */
export function RouteCompare({ parcel, chosen }: { parcel: ParcelId; chosen: string }) {
  return (
    <table className={styles.table} data-route-compare>
      <caption>Путь подарка до отгрузки</caption>
      <thead><tr><th scope="col">Место</th><th scope="col">До отгрузки</th><th scope="col">Кто найдёт</th></tr></thead>
      <tbody>
        {routeRows(parcel).map((row) => (
          <tr key={row.id} data-chosen={row.id === chosen || undefined} data-best={row.ok || undefined}>
            <th scope="row">{row.name}</th>
            <td>{row.metres} м</td>
            <td>{row.who}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
