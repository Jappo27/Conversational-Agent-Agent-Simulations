import React, { useState } from "react";
import { AutoComplete } from "primereact/autocomplete";

export default function AutocompleteDrop({ elements = [], value, onChange, placeholder = "Search..." }) {
  const [items, setItems] = useState(elements);

  const search = (event) => {
    let filtered = elements.filter(item =>
      item.toLowerCase().includes(event.query.toLowerCase())
    );
    setItems(filtered);
  };

  return (
    <div className="card flex justify-content-center">
      <AutoComplete
        value={value}
        suggestions={items}
        placeholder={placeholder}
        completeMethod={search}
        onChange={(e) => onChange(e.value)}
        dropdown
      />
    </div>
  );
}