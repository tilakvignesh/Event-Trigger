import React, { useState } from "react";

const TriggerForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    type: "api",
    schedule: "",
    payload: "",
    recurring: "false",
    test: "false",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payloadData = formData.payload ? JSON.parse(formData.payload) : {};
      const data = { ...formData, payload: payloadData };

      const response = await fetch("http://localhost:8000/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        console.log("Trigger created successfully!");
        window.close(); // ✅ Close the popup after submission
      } else {
        console.error("Error creating trigger:", await response.text());
      }
    } catch (error) {
      console.error("Invalid JSON in payload:", error);
    }
  };

  return (
    <div className="p-6 w-[350px]">
      <h2 className="text-lg font-bold mb-4">Create Trigger</h2>
      <form onSubmit={handleSubmit} className="flex flex-col space-y-2">
        <label>Name:</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="border p-2 rounded"
          required
        />

        <label>Type:</label>
        <select
          name="type"
          value={formData.type}
          onChange={handleChange}
          className="border p-2 rounded"
        >
          <option value="api">API</option>
          <option value="scheduled">Scheduled</option>
        </select>

        <label>Schedule (in seconds):</label>
        <input
          type="number"
          name="schedule"
          value={formData.schedule}
          onChange={handleChange}
          className="border p-2 rounded"
        />

        <label>Payload (JSON):</label>
        <input
          type="text"
          name="payload"
          value={formData.payload}
          onChange={handleChange}
          className="border p-2 rounded"
          placeholder='{"key": "value"}'
        />

        <label>Recurring:</label>
        <select
          name="recurring"
          value={formData.recurring}
          onChange={handleChange}
          className="border p-2 rounded"
        >
          <option value="false">False</option>
          <option value="true">True</option>
        </select>

        <label>Test:</label>
        <select
          name="test"
          value={formData.test}
          onChange={handleChange}
          className="border p-2 rounded"
        >
          <option value="false">False</option>
          <option value="true">True</option>
        </select>

        {/* Buttons */}
        <div className="flex justify-between">
          <button type="submit" className="px-4 py-2 bg-green-500 text-white rounded">
            Submit
          </button>
          <button
            type="button"
            className="px-4 py-2 bg-red-500 text-white rounded"
            onClick={() => window.close()}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default TriggerForm;
