import { useEffect } from "react";

export function usePageTitle(title: string | undefined) {
  useEffect(() => {
    if (title !== undefined) document.title = title;
  }, [title]);
}
