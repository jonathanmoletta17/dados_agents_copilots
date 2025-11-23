import { useState } from "react";
import DashboardDTIC from "./dtic/App";
import DashboardSIS from "./sis/App";
import SearchDTIC from "./dtic-search/App";
import SearchSIS from "./sis-search/App";
import Carregadores from "./carregadores/App";

type ActiveView = "dtic-dashboard" | "sis-dashboard" | "dtic-search" | "sis-search" | "carregadores";

export default function App() {
  const [activeView, setActiveView] = useState<ActiveView>("carregadores");

  return (
    <>
      {activeView === "dtic-dashboard" && (
        <DashboardDTIC 
          onSwitchToDashboard={() => setActiveView("sis-dashboard")}
          onSwitchToSearch={() => setActiveView("dtic-search")}
        />
      )}
      {activeView === "sis-dashboard" && (
        <DashboardSIS 
          onSwitchToDashboard={() => setActiveView("dtic-dashboard")}
          onSwitchToSearch={() => setActiveView("sis-search")}
        />
      )}
      {activeView === "dtic-search" && (
        <SearchDTIC 
          onSwitchToDashboard={() => setActiveView("dtic-dashboard")}
          onSwitchToSearch={() => setActiveView("sis-search")}
        />
      )}
      {activeView === "sis-search" && (
        <SearchSIS 
          onSwitchToDashboard={() => setActiveView("sis-dashboard")}
          onSwitchToSearch={() => setActiveView("dtic-search")}
        />
      )}
      {activeView === "carregadores" && (
        <Carregadores 
          onNavigate={(view) => setActiveView(view as ActiveView)}
        />
      )}
    </>
  );
}
