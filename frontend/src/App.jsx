import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import TriggerForm from "./components/Triggers/UploadTrigger";
import TriggersComponent from "./components/Triggers/GetTrigger";
import UpdateTrigger from "./components/Triggers/UpdateTrigger";
import Menu from "./components/Menu";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Menu />} />
        <Route path="/get-trigger" element={<TriggersComponent />} />
        <Route path="/post-trigger" element={<TriggerForm />} />
        <Route path="/update-trigger" element={<UpdateTrigger />} />

      </Routes>
    </Router>
  );
}

export default App;

