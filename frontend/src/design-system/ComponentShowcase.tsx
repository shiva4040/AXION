import React, { useState } from 'react';
import {
  MacButton,
  MacWindow,
  MacInput,
  MacTextarea,
  MacBadge,
  MacStatusBar,
  MacDialog,
  MacTable,
  Column,
} from './index';
import { Send, Paperclip } from 'lucide-react';

export const ComponentShowcase: React.FC = () => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const [textareaText, setTextareaText] = useState('What would you like to understand or solve?');

  const sampleData = [
    { id: 'SPEC-001', domain: 'Fluid Mechanics', formula: 'Q = ΔP / R_hyd', tier: 'TIER 1 // FACT', status: 'ACTIVE' },
    { id: 'SPEC-002', domain: 'Electrodynamics', formula: 'I = V / R', tier: 'TIER 4 // VALIDATED', status: 'VERIFIED' },
    { id: 'SPEC-003', domain: 'Thermodynamics', formula: 'J = -k ∇T', tier: 'TIER 3 // CONJECTURE', status: 'PENDING' },
    { id: 'SPEC-004', domain: 'Bioenergetics', formula: 'ΔG = ΔG° + RT ln Q', tier: 'TIER 1 // FACT', status: 'ACTIVE' },
  ];

  const columns: Column<(typeof sampleData)[0]>[] = [
    { header: 'ID', accessor: 'id', width: 'w-24' },
    { header: 'DOMAIN', accessor: 'domain' },
    {
      header: 'CONSTITUTIVE FORMULA',
      render: (row) => <span className="font-mono text-xs">{row.formula}</span>,
    },
    {
      header: 'EPISTEMIC TIER',
      render: (row) => (
        <MacBadge
          variant={
            row.tier.includes('VALIDATED')
              ? 'teal'
              : row.tier.includes('CONJECTURE')
              ? 'amber'
              : 'ink'
          }
          size="sm"
        >
          {row.tier}
        </MacBadge>
      ),
    },
    {
      header: 'STATUS',
      render: (row) => (
        <span className="font-bold text-[10px] text-[#252820] uppercase">{row.status}</span>
      ),
    },
  ];

  return (
    <div className="w-full max-w-5xl mx-auto p-4 sm:p-8 space-y-8 font-mono pb-16">
      {/* Title & Introduction */}
      <div className="border-b-2 border-[#252820] pb-4">
        <div className="text-[10px] uppercase font-bold tracking-widest text-[#777568] mb-1">
          DESIGN SYSTEM / AUDIT SPECIFICATION
        </div>
        <h1
          className="text-3xl sm:text-4xl text-[#252820] font-black tracking-normal"
          style={{ fontFamily: 'var(--font-slab)' }}
        >
          90s Classic Mac Component Library
        </h1>
        <p className="text-xs sm:text-sm text-[#5A584D] mt-1 font-mono leading-relaxed">
          Production design tokens and component specification matching the classic Macintosh System 7 aesthetic: 2px ink borders, hard offset shadows, warm paper, Alfa Slab One, and vermilion/teal accents.
        </p>
      </div>

      {/* 1. BUTTONS SPECIMEN */}
      <section className="space-y-4">
        <div className="text-xs font-bold uppercase tracking-wider text-[#252820] border-b border-[#252820]/30 pb-1">
          01. MACBUTTON VARIANTS & SIZES
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 bg-[#FDFBF7] border-2 border-[#252820] shadow-[4px_4px_0px_#252820] space-y-3">
            <span className="text-[10px] font-bold text-[#777568] block uppercase">
              VARIANTS
            </span>
            <div className="flex flex-wrap gap-2">
              <MacButton variant="paper">PAPER DEFAULT</MacButton>
              <MacButton variant="vermilion" rightIcon={<Send className="w-3.5 h-3.5" />}>
                SEND ↑
              </MacButton>
              <MacButton variant="teal">VALIDATED</MacButton>
              <MacButton variant="ink">SYSTEM INK</MacButton>
              <MacButton variant="outline">OUTLINE</MacButton>
            </div>
          </div>

          <div className="p-4 bg-[#FDFBF7] border-2 border-[#252820] shadow-[4px_4px_0px_#252820] space-y-3">
            <span className="text-[10px] font-bold text-[#777568] block uppercase">
              SIZES & STATES
            </span>
            <div className="flex flex-wrap items-center gap-2">
              <MacButton size="sm">SMALL (26px)</MacButton>
              <MacButton size="md">MEDIUM (34px)</MacButton>
              <MacButton size="lg">LARGE (42px)</MacButton>
              <MacButton isLoading>LOADING</MacButton>
              <MacButton disabled>DISABLED</MacButton>
            </div>
          </div>
        </div>
      </section>

      {/* 2. WINDOW SPECIMEN */}
      <section className="space-y-4">
        <div className="text-xs font-bold uppercase tracking-wider text-[#252820] border-b border-[#252820]/30 pb-1">
          02. MACWINDOW (SYSTEM 7 PINSTRIPE WINDOW)
        </div>

        <MacWindow
          title="QUERY.TXT"
          onClose={() => alert('Window close clicked')}
          onZoom={() => alert('Window zoom clicked')}
          footer={
            <>
              <MacButton variant="paper" size="sm" leftIcon={<Paperclip className="w-3.5 h-3.5" />}>
                ATTACH
              </MacButton>
              <MacButton variant="vermilion" size="sm" rightIcon={<Send className="w-3.5 h-3.5" />}>
                SEND ↑
              </MacButton>
            </>
          }
        >
          <div className="space-y-2">
            <p className="text-sm font-mono leading-relaxed">
              What would you like to understand or solve? Put your question to the desk.
            </p>
            <p className="text-xs text-[#777568]">
              This window container matches the core query box in the user's reference mockup with horizontal pinstripes, left square close box, center title pill, and 2px ink borders.
            </p>
          </div>
        </MacWindow>
      </section>

      {/* 3. INPUTS & TEXTAREAS */}
      <section className="space-y-4">
        <div className="text-xs font-bold uppercase tracking-wider text-[#252820] border-b border-[#252820]/30 pb-1">
          03. MACINPUT & MACTEXTAREA
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <MacInput
            label="RESEARCH TOPIC"
            placeholder="e.g. Poiseuille Continuum Transport"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            helperText="Enter a domain concept or physical law"
          />

          <MacInput
            label="AUTHENTICATION CODE"
            placeholder="Enter token"
            error="INVALID TOKEN OR SIGNATURE"
          />

          <div className="sm:col-span-2">
            <MacTextarea
              label="FORMULATE SCIENTIFIC PROPOSITION"
              value={textareaText}
              onChange={(e) => setTextareaText(e.target.value)}
              rows={3}
            />
          </div>
        </div>
      </section>

      {/* 4. BADGES & STAMPS */}
      <section className="space-y-4">
        <div className="text-xs font-bold uppercase tracking-wider text-[#252820] border-b border-[#252820]/30 pb-1">
          04. MACBADGE (STAMPS & EPISTEMIC TIERS)
        </div>

        <div className="flex flex-wrap gap-3 items-center p-4 bg-[#FDFBF7] border-2 border-[#252820] shadow-[4px_4px_0px_#252820]">
          <MacBadge variant="vermilion" isStamp>
            INTELLIGENCE
          </MacBadge>
          <MacBadge variant="teal">TIER 4 // VALIDATED</MacBadge>
          <MacBadge variant="amber">TIER 3 // CONJECTURED</MacBadge>
          <MacBadge variant="ink">TIER 1 // DOCUMENTED FACT</MacBadge>
          <MacBadge variant="paper">CATALOG SPECIMEN</MacBadge>
        </div>
      </section>

      {/* 5. DATA LEDGER TABLE */}
      <section className="space-y-4">
        <div className="text-xs font-bold uppercase tracking-wider text-[#252820] border-b border-[#252820]/30 pb-1">
          05. MACTABLE (ARCHIVAL LEDGER)
        </div>

        <MacTable
          columns={columns}
          data={sampleData}
          keyExtractor={(row) => row.id}
          onRowClick={(row) => alert(`Selected ${row.id}`)}
        />
      </section>

      {/* 6. MODAL DIALOG */}
      <section className="space-y-4">
        <div className="text-xs font-bold uppercase tracking-wider text-[#252820] border-b border-[#252820]/30 pb-1">
          06. MACDIALOG (CONFIRMATION / ALERT MODAL)
        </div>

        <MacButton onClick={() => setDialogOpen(true)}>
          OPEN ALERT.DLG MODAL
        </MacButton>

        <MacDialog
          isOpen={dialogOpen}
          onClose={() => setDialogOpen(false)}
          title="CONFIRM_EXECUTION.DLG"
          footer={
            <div className="w-full flex justify-end gap-2">
              <MacButton variant="outline" size="sm" onClick={() => setDialogOpen(false)}>
                CANCEL
              </MacButton>
              <MacButton variant="vermilion" size="sm" onClick={() => setDialogOpen(false)}>
                EXECUTE CONFIRMATION
              </MacButton>
            </div>
          }
        >
          <div className="space-y-3">
            <h3 className="font-bold text-sm text-[#252820]">
              Execute Empirical Cross-Domain Derivation?
            </h3>
            <p className="text-xs text-[#5A584D] leading-relaxed">
              This operation triggers the 8-stage AXION cognitive pipeline to verify dimensional invariants and evaluate Gentner structure-mapping hypotheses.
            </p>
          </div>
        </MacDialog>
      </section>

      {/* Bottom Status Bar Demo */}
      <MacStatusBar statusText="READY // 90S MAC DESIGN SYSTEM ACTIVE" statusVariant="ready" />
    </div>
  );
};
