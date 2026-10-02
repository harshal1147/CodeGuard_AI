'use client';

import Editor from '@monaco-editor/react';

export function CodeEditor({
  value,
  language,
  onChange,
}: {
  value: string;
  language: string;
  onChange?: (value: string) => void;
}) {
  return (
    <div className="h-[420px] overflow-hidden rounded-xl border border-slate-700 bg-[#0b1120]">
      <Editor
        height="100%"
        defaultLanguage={language}
        language={language}
        value={value}
        theme="vs-dark"
        onChange={(nextValue) => onChange?.(nextValue ?? '')}
        options={{
          minimap: { enabled: true },
          scrollBeyondLastLine: false,
          fontSize: 14,
          lineNumbers: 'on',
          roundedSelection: false,
          automaticLayout: true,
          wordWrap: 'on',
        }}
      />
    </div>
  );
}
