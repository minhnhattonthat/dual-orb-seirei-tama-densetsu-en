; Dual Orb English: variable-width font for the text engine (docs/re/vwf.md).
; Every glyph the engine draws goes through $00:AEB6 (code in A, target cell at [$BB] in the BG3 tilemap buffer
; $7F:F000). This replaces it: glyphs are drawn into pool tiles (the old kana/Latin glyph tiles, 2 per cell,
; top + bottom) shadowed in WRAM at SHADOW + tile*16 and sent to VRAM by vwf_nmi from its own upload ring.
; Pool tiles are handed out round-robin; when none is free, a sweep of the tilemap buffer frees every tile no
; cell shows. Static glyphs (flags 1: page arrows, cursor, leader dot, cell space) keep their original tiles and
; snap to the next cell. The engine's column $0E0B is kept so that its next [$BB] is the cell after the pen.
lorom

incsrc "../build/vwf/defs.asm"

!SHADOW   = $E000         ; $7E:E000 + tile*16, tiles < $180 (free WRAM: tools/lua/wramuse.lua)
!SIG      = $F800         ; WRAM vars, bank $7E (DB = $7E inside the VWF)
!PENCELL  = $F802         ; tilemap address of the cell the pen is in
!PENSUB   = $F804         ; pen px inside that cell (0 = at its left edge, nothing open)
!OPENT    = $F806         ; pool pair drawn in the pen cell, $FFFF none
!ROVER    = $F808
!CODE     = $F80A
!WIDTH    = $F80C
!PAL      = $F80E
!TL       = $F810
!TR       = $F812
!B        = $F814         ; [$BB] at entry
!SUBOFS   = $F816
!GCDONE   = $F818
!TMPV     = $F81A
!TMPS     = $F81C
!DUMMY    = $F840         ; 32 bytes: render target when no right cell
!USED     = $F860         ; one byte per pool pair (182)
!PEND     = $F920         ; one byte per pool pair: queued for upload, not yet sent
!CELLX    = $F828
!TILE     = $F82A
!NTILE    = $F82C         ; NMI's own temp
!BUSY     = $F82E         ; nonzero while enqueue edits the ring: the NMI skips that frame
!GDMA     = $F832         ; byte, nonzero while the game's queue flush is between VMAIN/address and its DMA
!INDRAW   = $F834         ; nonzero while vwf_draw runs (an NMI there may see a pair half rendered)
!SKIPOPEN = $F836         ; upload: 1 hold the pen's open pair (more glyphs may join it), 2 also the pairs in render
!DRAWN    = $F830         ; nonzero: vwf_draw ran since the last NMI (the main thread may be mid-redraw)
!LIMIT    = $F838         ; upload: bytes of the current ring entry it may send now
!CUR      = $F83A         ; upload: ring entry being sent (held entries are passed over, popped once sent)
!QEND     = $F83C         ; upload: QTAIL when it started (held entries moved to the tail are not met again)
!SENT     = $7F8F00       ; byte per pool pair (to $8FB5): sent to VRAM since alloc handed it out (else VRAM shows junk)
!QHEAD    = $F820         ; upload ring: byte offsets 0-$1FE into QV/QS/QN (256 runs)
!QTAIL    = $F822
!CHUNK    = $F824
!BUDGET   = $F826
!NMIBYTES = $0400         ; pool tiles uploaded per frame (32 cells), after the game's own DMA
!IDLEBYTES = $1000        ; per NMI with no game frame ready (vblank from line 225: ~6 KB of DMA)
!CHUNKMAX = $0040        ; bytes per DMA, so one never runs far past the end of vblank
!MEMO     = $7F8900       ; byte per cell of $7F:F000-$F7FF (offset >> 1): the pool pair it last showed, FF none
!OWNER    = $7F8D00       ; word per pool pair (to $8E6B): the cell it was last handed to (blanked-and-redrawn rows reuse it)
!QV       = $FA00         ; VRAM word address
!QS       = $FC00         ; source (bank $7E)
!QN       = $FE00         ; bytes left (a multiple of 32: whole pairs)

org $00AEB6               ; old glyph drawer (42 bytes; callers JSR here and expect A 16-bit on return)
	php
	jsl vwf_draw
	plp
	rep #$20
	rts
assert pc() <= $00AEE0

org $0080A9               ; NMI: JSL $00E388 -> upload queued tiles first
	jsl vwf_nmi

org $0085E8               ; NMI timer (every NMI, also the ones with no game frame ready): REP #$30; INC $F1
	jsl vwf_idle

; The game's DMA-queue flush also runs from the main thread (field loads, after battles). An NMI upload between its
; VMAIN/VRAM-address writes and its DMA sent the game's tiles to our address and left the map corrupt (issue #1):
; flag each entry's VMAIN .. DMA, and upload skips while it is set.
org $009795               ; was: SEP #$20; LDA $05 (D = the queue entry; BEQ after uses the flags)
	jsl gdma_on
org $0097C3               ; was: LDA #$80; STA $2115 (after the entry's DMA)
	jsl gdma_off
	nop

org $B08000
vwf_draw:
	phb
	rep #$30
	and #$00FF
	sta.l $7E0000+!CODE
	pei ($00)
	pei ($02)
	pei ($04)
	pei ($06)
	pea $7E7E
	plb
	plb
	sep #$20
	lda #$01
	sta.l $00420D         ; FastROM for this bank ($B0); the game's code in $00-$3F is unaffected
	rep #$20
	lda.w !SIG
	cmp #$5756
	beq +
	jsr init
+	lda #$0001
	sta.w !DRAWN
	sta.w !INDRAW
	lda.w $0E32
	and #$FF00
	asl
	asl
	ora #$2000
	sta.w !PAL
	lda $BB
	sta.w !B
	; continue the open cell when the engine asks for the cell right after it
	lda.w !PENSUB
	beq .fresh
	lda.w !PENCELL
	inc
	inc
	cmp.w !B
	beq .go
.fresh
	lda.w !B
	sta.w !PENCELL
	stz.w !PENSUB
	lda #$FFFF
	sta.w !OPENT
.go
	ldx.w !CODE
	lda.l vwf_widths,x
	and #$00FF
	sta.w !WIDTH
	lda.l vwf_flags,x
	and #$00FF
	beq .glyph
	cmp #$0001
	bne +
	jmp .static
+	jmp .space

.glyph
	; left cell: the open pair if the tilemap still shows it, else a fresh one
	lda.w !OPENT
	cmp #$FFFF
	beq .newl
	ldx.w !PENCELL
	lda.l $7F0000,x
	and #$03FF
	cmp.w !OPENT
	beq .havel
.newl
	ldx.w !PENCELL
	jsr getpair
	sta.w !OPENT
.havel
	lda.w !OPENT
	sta.w !TL
	lda #$FFFF
	sta.w !TR
	lda.w !PENSUB
	clc
	adc.w !WIDTH
	cmp #$0009
	bcc .render
	ldx.w !PENCELL
	inx
	inx
	jsr getpair
	sta.w !TR
.render
	lda.w !TL
	asl
	asl
	asl
	asl
	clc
	adc #!SHADOW
	sta $03
	lda #!DUMMY
	ldx.w !TR
	cpx #$FFFF
	beq +
	txa
	asl
	asl
	asl
	asl
	clc
	adc #!SHADOW
+	sta $05
	lda.w !CODE
	asl
	asl
	asl
	asl
	asl
	clc
	adc.w #vwf_font&$FFFF
	sta $00
	sep #$20
	lda.b #vwf_font>>16
	sta $02
	rep #$20
	lda.w !PENSUB
	xba
	asl
	sta.w !SUBOFS
	ldy #$0000
.row
	sep #$20
	lda [$00],y
	beq .next
	rep #$20
	and #$00FF
	asl
	adc.w !SUBOFS
	tax
	sep #$20
	lda.l vwf_shift,x
	ora ($03),y
	sta ($03),y
	lda.l vwf_shift+1,x
	beq .next
	ora ($05),y
	sta ($05),y
.next
	rep #$20
	iny
	cpy #$0020
	bne .row
	lda.w !TL
	jsr enqueue
	lda.w !TR
	cmp #$FFFF
	beq +
	jsr enqueue
+	lda.w !PENSUB
	clc
	adc.w !WIDTH
	cmp #$0008
	bcc .same
	sbc #$0008
	sta.w !PENSUB
	lda.w !PENCELL
	inc
	inc
	sta.w !PENCELL
	lda.w !TR
	sta.w !OPENT
	bra .finish
.same
	sta.w !PENSUB
	bra .finish

.static                   ; original tiles at the engine's cell (after the open one, if any)
	lda.w !CODE
	asl
	asl
	tax
	ldy.w !B
	lda.l $00B0A2,x
	ora.w !PAL
	tyx
	sta.l $7F0000,x
	lda.w !CODE
	asl
	asl
	tax
	lda.l $00B0A4,x
	ora.w !PAL
	tyx
	sta.l $7F0040,x
	tya
	inc
	inc
	sta.w !PENCELL
	stz.w !PENSUB
	bra .finish

.space                    ; word space: no tiles, blanks any cell it enters
	lda.w !PENSUB
	bne .spmid
	ldx.w !PENCELL
	jsr blankcell
	lda #$FFFF
	sta.w !OPENT
	lda.w !WIDTH
	bra .spadd
.spmid
	clc
	adc.w !WIDTH
	cmp #$0008
	bcc .spadd
	sbc #$0008
	pha
	lda.w !PENCELL
	inc
	inc
	sta.w !PENCELL
	lda #$FFFF
	sta.w !OPENT
	pla
	beq .spadd
	pha
	ldx.w !PENCELL
	jsr blankcell
	pla
.spadd
	sta.w !PENSUB

.finish                   ; $0E0B += (next cell - B) / 2
	lda.w !PENSUB
	beq +
	lda #$0002
+	clc
	adc.w !PENCELL
	sec
	sbc.w !B
	lsr
	clc
	adc.w $0E0B
	sta.w $0E0B
	lda.w !PENSUB
	bne +
	lda #$FFFF
	sta.w !OPENT
+	stz.w !INDRAW
	pla
	sta $06
	pla
	sta $04
	pla
	sta $02
	pla
	sta $00
	plb
	rtl

; X = cell: a cleared pair shown there -> A = its top tile. A redrawn cell keeps the pool pair it already shows
; (no churn: menus redraw the same fields often), else a free pair is allocated.
getpair:
	stx.w !CELLX
	lda.l $7F0000,x
	and #$03FF
	cmp #$0180
	bcs .alloc
	sta.w !TILE
	tax
	lda.l vwf_tilepair,x
	and #$00FF
	cmp #$00FF
	beq .alloc
	tay
	asl
	tax
	lda.l vwf_pairs,x
	cmp.w !TILE
	bne .alloc                ; the cell shows a pair's bottom tile: not ours to reuse
	tyx
	sep #$20
	lda #$01
	sta.w !USED,x
	rep #$20
	lda.w !TILE
	brl .have
.alloc                    ; the cell shows no pool pair (e.g. its row was blanked): the pair it showed last, if
	lda.w !CELLX              ; no other cell has been handed it since, else a free one (top 32x32 screen only)
	and #$0FFF
	cmp #$0800
	bcs .plain
	lsr
	tax
	lda.l !MEMO,x
	and #$00FF
	cmp #$00FF
	beq .free
	tay
	asl
	tax
	lda.l !OWNER,x
	cmp.w !CELLX
	bne .free
	tyx
	sep #$20
	lda #$01
	sta.w !USED,x
	rep #$20
	txa
	asl
	tax
	lda.l vwf_pairs,x
	sta.w !TILE
	bra .have
.free
	jsr alloc
	sta.w !TILE
	tax
	lda.l vwf_tilepair,x      ; remember: cell -> pair, pair -> cell
	and #$00FF
	pha
	asl
	tax
	lda.w !CELLX
	sta.l !OWNER,x
	and #$0FFF
	lsr
	tax
	pla
	sep #$20
	sta.l !MEMO,x
	rep #$20
	lda.w !TILE               ; clearpair takes the tile
	bra .have
.plain
	jsr alloc
	sta.w !TILE
	tax                       ; claim it, so no top-screen cell's memo takes it back while this cell shows it (crawl)
	lda.l vwf_tilepair,x
	and #$00FF
	asl
	tax
	lda.w !CELLX
	sta.l !OWNER,x
	lda.w !TILE
.have
	jsr clearpair
	ldx.w !CELLX
	lda.w !TILE
	jsr putcell
	lda.w !TILE
	rts

; A = tile -> cell X (tilemap address, bank $7F) shows pair A
putcell:
	ora.w !PAL
	sta.l $7F0000,x
	inc
	sta.l $7F0040,x
	rts

blankcell:
	lda.l $00B19E             ; glyph-table entry of the cell space (3F)
	ora.w !PAL
	sta.l $7F0000,x
	lda.l $00B1A0
	ora.w !PAL
	sta.l $7F0040,x
	rts

; A = tile: zero its pair's shadow
clearpair:
	asl
	asl
	asl
	asl
	tax
	stz.w !SHADOW+$00,x
	stz.w !SHADOW+$02,x
	stz.w !SHADOW+$04,x
	stz.w !SHADOW+$06,x
	stz.w !SHADOW+$08,x
	stz.w !SHADOW+$0A,x
	stz.w !SHADOW+$0C,x
	stz.w !SHADOW+$0E,x
	stz.w !SHADOW+$10,x
	stz.w !SHADOW+$12,x
	stz.w !SHADOW+$14,x
	stz.w !SHADOW+$16,x
	stz.w !SHADOW+$18,x
	stz.w !SHADOW+$1A,x
	stz.w !SHADOW+$1C,x
	stz.w !SHADOW+$1E,x
	rts

; -> A = top tile of a free pool pair (marked used)
alloc:
	stz.w !GCDONE
.again
	ldx.w !ROVER
	ldy.w #!POOL_N
.scan
	sep #$20
	lda.w !USED,x
	rep #$20
	and #$00FF
	beq .found
	inx
	cpx.w #!POOL_N
	bcc +
	ldx #$0000
+	dey
	bne .scan
	lda.w !GCDONE
	bne .force                ; shortcut: pool full even after a sweep -> reuse the rover's pair (garbles one cell)
	inc.w !GCDONE
	jsr gc
	bra .again
.force
	ldx.w !ROVER
.found
	sep #$20
	lda #$01
	sta.w !USED,x
	lda #$00
	sta.l !SENT,x
	rep #$20
	txa
	inc
	cmp.w #!POOL_N
	bcc +
	lda #$0000
+	sta.w !ROVER
	txa
	asl
	tax
	lda.l vwf_pairs,x
	rts

; free every pool pair the tilemap buffer doesn't show
gc:
	ldx #$0000
	sep #$20
-	stz.w !USED,x
	inx
	cpx.w #!POOL_N
	bne -
	rep #$20
	phb
	pea $7F7F
	plb
	plb
	ldy #$0000
.l	lda $F000,y
	and #$03FF
	cmp #$0180
	bcs .n
	tax
	sep #$20
	lda.l vwf_tilepair,x
	cmp #$FF
	beq .s
	rep #$20
	and #$00FF
	tax
	sep #$20
	lda #$01
	sta.l $7E0000+!USED,x
.s	rep #$20
.n	iny
	iny
	cpy #$1000
	bne .l
	plb
	rts

; A = top tile: queue its pair (32 bytes) for VRAM, merging with the last entry when contiguous.
; Own ring (not the game's $0661 queue: bulk tiles there ran the NMI past vblank and the game's tilemap rows after
; them were lost). vwf_nmi drains it after the game's uploads, only while the V counter is inside vblank.
enqueue:
	inc.w !BUSY               ; an NMI mid-merge could retire the entry being extended: the tile and its PEND were lost
	jsr .q
	stz.w !BUSY
	rts
.q
	tax
	sep #$20
	lda.l vwf_tilepair,x
	rep #$20
	and #$00FF
	tay
	lda.w !PEND,y             ; already waiting: the NMI sends whatever the shadow holds then
	and #$00FF
	beq +
	rts
+	sep #$20
	lda #$01
	sta.w !PEND,y
	rep #$20
	txa
	asl
	asl
	asl
	clc
	adc #$2000
	sta.w !TMPV
	asl
	clc
	adc #!SHADOW-$4000
	sta.w !TMPS
	ldx.w !QTAIL
	cpx.w !QHEAD
	beq .new
	txa
	dec
	dec
	and #$01FE
	tay
	lda.w !QN,y
	lsr
	clc
	adc.w !QV,y
	cmp.w !TMPV
	bne .new
	lda.w !QN,y
	clc
	adc.w !QS,y
	cmp.w !TMPS
	bne .new
	lda.w !QN,y
	clc
	adc #$0020
	sta.w !QN,y
	rts
.new
	txa
	inc
	inc
	and #$01FE
	cmp.w !QHEAD
	beq .drop                 ; can't happen: PEND keeps it to <= 182 runs of 256
	pha
	lda.w !TMPV
	sta.w !QV,x
	lda.w !TMPS
	sta.w !QS,x
	lda #$0020
	sta.w !QN,x
	pla
	sta.w !QTAIL
.drop
	rts

; ring entry X just sent CHUNK bytes from its QV: those pairs may be queued again
unpend:
	phx
	lda.w !QV,x
	sec
	sbc #$2000
	lsr
	lsr
	lsr
	sta.w !NTILE
	lda.w !CHUNK
	lsr
	lsr
	lsr
	lsr
	lsr
	tay
-	ldx.w !NTILE
	lda.l vwf_tilepair,x
	and #$00FF
	tax
	sep #$20
	stz.w !PEND,x
	lda #$01
	sta.l !SENT,x
	rep #$20
	inc.w !NTILE
	inc.w !NTILE
	dey
	bne -
	plx
	rts

; NMI, in place of its JSL $00E388 (after the game's own DMA): upload queued pool tiles while in vblank
vwf_nmi:
	php
	rep #$30
	lda #$0000                ; the game readied this frame: its drawing is complete
	sta.l $7E0000+!DRAWN
	sta.l $7E0000+!SKIPOPEN
	lda #!NMIBYTES
	jsr upload
	plp
	jml $00E388

; NMI timer: menus ready a game frame only every ~5 NMIs, and the idle ones have the whole vblank free (the game's
; DMA after line 225 left the hook ~2 lines). The game's main-thread queue flush is fenced by gdma_on/off.
; A redrawn cell's pair is cleared and re-rendered glyph by glyph, and sending it half done showed half cells for a
; frame (battle panel, issue #1). So while the main thread is drawing (vwf_draw ran since the last NMI) the pen's
; open pair waits, and when this NMI cut into vwf_draw also the pairs it is rendering (SKIPOPEN 1 / 2); only pairs
; VRAM already shows right (!SENT). Skipping the whole upload instead starved menus and shops, which draw for ~5
; NMIs a frame (stale glyphs for seconds, r6 tour). Without the open-pair hold the battle panel flickers again.
vwf_idle:
	rep #$30
	lda.l $7E0000+!INDRAW
	beq +
	lda #$0002                ; DRAWN stays set: the draw resumes after this NMI
	bra ++
+	lda.l $7E0000+!DRAWN
	pha
	lda #$0000
	sta.l $7E0000+!DRAWN
	pla
++	sta.l $7E0000+!SKIPOPEN
	lda #!IDLEBYTES
	jsr upload
	rep #$30
	inc $F1                   ; replaced: DP = 0 in the NMI
	rtl

gdma_on:
	sep #$20
	lda #$01
	sta.l $7E0000+!GDMA
	lda $05
	rtl

gdma_off:
	lda #$80
	sta.l $002115
	lda #$00
	sta.l $7E0000+!GDMA
	rtl

; A = byte budget: send queued pool tiles while in vblank
upload:
	php
	sep #$20
	pha
	lda.l $7E0000+!GDMA       ; WRAM is random at power-on: the boot flush (f26) clears it before any glyph
	beq +
	pla
	plp
	rts
+	pla
	rep #$30
	sta.l $7E0000+!BUDGET
	phb
	pea $7E7E
	plb
	plb
	lda.l $004300             ; the game's code may count on channel 0's settings: keep them
	pha
	lda.l $004302
	pha
	lda.l $004304
	pha
	lda.l $004306
	pha
	sep #$20
	lda #$80
	sta.l $002115
	lda #$01
	sta.l $004300
	lda #$18
	sta.l $004301
	lda #$7E
	sta.l $004304
	rep #$20
	lda.w !SIG                ; WRAM is random until the first glyph runs init
	cmp #$5756
	bne .busy
	lda.w !BUSY
	bne .busy
	lda.w !QHEAD
	sta.w !CUR
	lda.w !QTAIL
	sta.w !QEND
	bra .loop
.busy
	jmp .done
.out
	jmp .pop
.loop
	ldx.w !CUR
	cpx.w !QEND
	beq .out
	lda.w !BUDGET             ; cap per NMI (latching the H/V counters via $2137 hung the game at file select)
	beq .out
	sep #$20
	lda.l $004212             ; the hook often starts near line 257: stop when vblank ends, VRAM writes outside it are lost
	rep #$20
	bpl .out
	lda.w !QN,x
	beq .next                 ; sent, waiting for the entries before it
	sta.w !LIMIT
	lda.w !SKIPOPEN           ; a pair still being drawn: send the run only up to it, the rest on a later NMI
	beq .send
	cmp #$0002
	bne .open
	lda.w !TILE
	jsr holds
	lda.w !TL
	jsr holds
	lda.w !TR
	jsr holds
.open
	lda.w !PENSUB
	beq +
	lda.w !OPENT
	jsr holds
+	lda.w !LIMIT
	bne .send
.next                     ; held: go on with the later entries (stopping here starved them, r7 shop fade-in)
	cpx.w !QHEAD
	bne .skip
	lda.w !QN,x               ; the head: retire it if sent, else move what is held to the tail (past QEND)
	beq .popped
	ldy.w !QTAIL
	tya
	inc
	inc
	and #$01FE
	cmp.w !QHEAD
	beq .skip                 ; full: leave it
	pha
	lda.w !QV,x
	sta.w !QV,y
	lda.w !QS,x
	sta.w !QS,y
	lda.w !QN,x
	sta.w !QN,y
	pla
	sta.w !QTAIL
.popped
	txa
	inc
	inc
	and #$01FE
	sta.w !QHEAD
	sta.w !CUR
	jmp .loop
.skip
	txa
	inc
	inc
	and #$01FE
	sta.w !CUR
	jmp .loop
.send
	lda #!CHUNKMAX
	cmp.w !LIMIT
	bcc +
	lda.w !LIMIT
+	cmp.w !BUDGET
	bcc +
	lda.w !BUDGET
+	sta.w !CHUNK
	lda.w !BUDGET
	sec
	sbc.w !CHUNK
	sta.w !BUDGET
	lda.w !CHUNK             ; chunk
	sta.l $004305
	lda.w !QV,x
	sta.l $002116
	lda.w !QS,x
	sta.l $004302
	sep #$20
	lda #$01
	sta.l $00420B
	lda.l $004212             ; vblank ended during the DMA: its tail was dropped, so keep the entry to resend it
	bmi +
	jmp .done
+	rep #$20
	jsr unpend
	lda.w !CHUNK
	lsr
	clc
	adc.w !QV,x
	sta.w !QV,x
	lda.w !CHUNK
	clc
	adc.w !QS,x
	sta.w !QS,x
	lda.w !QN,x
	sec
	sbc.w !CHUNK
	sta.w !QN,x
	jmp .loop
.pop                      ; retire the sent entries at the head
	ldx.w !QHEAD
	cpx.w !QTAIL
	beq .done
	lda.w !QN,x
	bne .done
	txa
	inc
	inc
	and #$01FE
	sta.w !QHEAD
	bra .pop
.done
	rep #$20
	pla
	sta.l $004306
	pla
	sta.l $004304
	pla
	sta.l $004302
	pla
	sta.l $004300
	plb
	plp
	rts

; A = top tile ($FFFF none), X = ring entry: if the entry's run [QV, QV + LIMIT/2) holds its pair, LIMIT = the
; bytes before it
holds:
	cmp #$FFFF
	beq +
	sta.w !NTILE
	phx
	tax
	lda.l vwf_tilepair,x
	and #$00FF
	tax
	lda.l !SENT,x
	plx
	and #$00FF
	beq +                     ; never sent since handed out: VRAM shows junk there, a part drawn beats it
	lda.w !NTILE
	asl
	asl
	asl
	clc
	adc #$2000
	sec
	sbc.w !QV,x
	bcc +
	asl
	cmp.w !LIMIT
	bcs +
	sta.w !LIMIT
+	rts

init:
	ldx #$0000
	sep #$20
-	stz.w !USED,x
	stz.w !PEND,x
	lda #$00
	sta.l !SENT,x
	inx
	cpx.w #!POOL_N
	bne -
	rep #$20
	lda #$FFFF                ; no cell remembers a pair yet
	ldx #$03FE
-	sta.l !MEMO,x
	dex
	dex
	bpl -
	stz.w !ROVER
	stz.w !PENSUB
	stz.w !QHEAD
	stz.w !QTAIL
	stz.w !BUSY
	lda #$FFFF
	sta.w !OPENT
	sta.w !PENCELL
	lda #$5756
	sta.w !SIG
	rts

vwf_widths:   incbin "../build/vwf/widths.bin"
vwf_flags:    incbin "../build/vwf/flags.bin"
vwf_pairs:    incbin "../build/vwf/pairs.bin"
vwf_tilepair: incbin "../build/vwf/tilepair.bin"
assert pc() <= $B0A000
org $B0A000
vwf_font:     incbin "../build/vwf/font.bin"     ; 8 KB, $B0:A000-$BFFF
vwf_shift:    incbin "../build/vwf/shift.bin"    ; 4 KB, $B0:C000-$CFFF
assert pc() <= $B0D000

incsrc "names.asm"
incsrc "namechart.asm"
incsrc "crawl.asm"
incsrc "buttons.asm"
incsrc "compass.asm"
incsrc "controller.asm"
assert pc() <= $B0FFFF
incsrc "menus.asm"
