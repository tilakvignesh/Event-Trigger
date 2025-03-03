import { useState } from "react";

const UpdateTrigger = () => {
  const [triggerId, setTriggerId] = useState("");
  const [name, setName] = useState("");
  const [schedule, setSchedule] = useState("");
  const [recurring, setRecurring] = useState(false);
  const [payload, setPayload] = useState("{}"); // JSON as a string

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        const body = {}
        if(name!=="") {
            body.name = name;
        }
        if(schedule!=="") {
            body.schedule = schedule;
        }
        if(payload!=="{}") {
            body.payload = payload;
        }
      const response = await fetch(`http://localhost:8000/triggers/${triggerId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();
      alert(`Response: ${JSON.stringify(data)}`);

      // Clear form
      setTriggerId("");
      setName("");
      setSchedule("");
      setRecurring(false);
      setPayload("{}");
    } catch (error) {
      console.error("Error updating trigger:", error);
      alert("Failed to update trigger");
    }
  };

  return (
    <div>
      <h2>Update Trigger</h2>
      <form onSubmit={handleSubmit}>
        <label>Trigger ID:</label>
        <input type="text" value={triggerId} onChange={(e) => setTriggerId(e.target.value)} required />

        <label>Name:</label>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} />

        <label>Schedule (seconds):</label>
        <input type="number" value={schedule} onChange={(e) => setSchedule(e.target.value)} />

        <label>Payload (JSON):</label>
        <input type="text" value={payload} onChange={(e) => setPayload(e.target.value)} />

        <label>Recurring:</label>
        <select value={recurring} onChange={(e) => setRecurring(e.target.value)}>
          <option value="false">False</option>
          <option value="true">True</option>
        </select>

        <button type="submit">Update Trigger</button>
      </form>
    </div>
  );
};

export default UpdateTrigger;
