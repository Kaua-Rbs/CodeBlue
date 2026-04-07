import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { ActionsPage } from "../pages/ActionsPage";
import { CommandCenterPage } from "../pages/CommandCenterPage";
import { WardsPage } from "../pages/WardsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <CommandCenterPage /> },
      { path: "actions", element: <ActionsPage /> },
      { path: "wards", element: <WardsPage /> },
    ],
  },
]);
