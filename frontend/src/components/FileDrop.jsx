
import React from 'react';

export default function FileDrop({ multi, accept, onFiles }) {
  const [dragOver, setDragOver] = React.useState(false);
  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const list = Array.from(e.dataTransfer.files || []);
    onFiles(multi ? list : list.slice(0,1));
  };
  return (
    <div
      className={(dragOver ? "border-primary-600 bg-primary-50 " : "border-gray-300 bg-gray-50 ") +
                  "border-2 border-dashed rounded-2xl p-6 text-center transition"}
      onDragOver={(e)=>{e.preventDefault(); setDragOver(true)}}
      onDragLeave={()=>setDragOver(false)}
      onDrop={onDrop}
    >
      <p className="mb-2 font-medium">Drag & drop {multi ? 'file(s)' : 'a file'} here</p>
      <p className="text-sm text-gray-500 mb-4">or click to choose</p>
      <input
        type="file"
        multiple={multi}
        accept={accept}
        onChange={(e)=> onFiles(Array.from(e.target.files || []))}
        className="block w-full text-sm text-gray-900 file:mr-4 file:py-2 file:px-4
                   file:rounded-full file:border-0 file:font-semibold
                   file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200
                   cursor-pointer"
      />
    </div>
  );
}
