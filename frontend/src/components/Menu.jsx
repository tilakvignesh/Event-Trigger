import React from "react";

const Menu = () => {
  const openGetTriggerPopup = () => {
    const popup = window.open(
      "/get-trigger",
      "TriggersComponent",
      "width=400,height=600,left=100,top=100"
    );

    if (!popup) {
      alert("Popup blocked! Please allow popups.");
    }
  };


  const openPostTriggerPopup = () => {
    const popup = window.open(
      "/post-trigger",
      "TriggerForm",
      "width=400,height=600,left=100,top=100"
    );

    if (!popup) {
      alert("Popup blocked! Please allow popups.");
    }
  };

  const openUpdateTriggerPopup = () => {
    const popup = window.open(
      "/update-trigger",
      "UpdateTrigger",
      "width=400,height=600,left=100,top=100"
    );

    if (!popup) {
      alert("Popup blocked! Please allow popups.");
    }
  };


  return (
    <div className="p-4">
      <button
        className="px-4 py-2 btn-dark text-white rounded"
        onClick={openGetTriggerPopup}
      >
        Get Triggers
      </button>
      <button
        className="px-4 py-2 btn-dark text-white rounded"
        onClick={openPostTriggerPopup}
      >
        Post Trigger
      </button>
      <button
        className="px-4 py-2 btn-dark text-white rounded"
        onClick={openUpdateTriggerPopup}
      >
        Update Trigger
      </button>
    </div>
  );
};

export default Menu;
