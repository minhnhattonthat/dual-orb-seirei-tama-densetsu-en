; English name-entry chart (rename screen, field sub-mode 3; docs/re/text.md §Name entry). The game copies a stored
; tilemap per page (kana glyph tiles, now VWF pool tiles) to $7F:F000 at $21:E981; this blanks the grid and the
; button row and prints the page's letters and labels through the text engine instead. Picks read the English grid
; (tools/namechart.py) and stop at HERO_PX wide. Sites verified against the original bytes by tests/test_vwf.py.

!CAP  = 42                ; tools/wrap.py HERO_PX: the width every party-name slot is laid out for
!CSUM = $7EF81C           ; VWF temp (!TMPS), free outside a glyph draw

org $21E623               ; cursor rows 0-3 (+ buttons) on every page, not only the Latin one
	nop
	nop
org $21E719               ; ADC #grid: page*90 + row*10 + col
	dw chart_grid
org $21E739               ; SEP #$30 / LDA ($00)
	jsl chart_pick
org $21E985               ; LDA $13D3 / ORA #$FFE0, after the page tilemap is in the buffer
	jsl chart_draw
	nop
	nop

org $B0D000
chart_draw:               ; A X Y 16-bit, DB = $21
	lda.w #$216A              ; the blank cell the stored tilemaps use
	ldx.w #(6*32+6)*2
.row:
	ldy.w #20
-	sta.l $7FF000,x
	inx
	inx
	dey
	bne -
	pha
	txa
	clc
	adc.w #24             ; to column 6 of the next row
	tax
	pla
	cpx.w #(26*32)*2
	bcc .row
	lda $32
	asl
	tax
	lda.l chart_text,x
	clc
	adc.w #chart_text
	sta $B3
	lda.w #chart_text>>16
	sta $B5
	ldx.w #6
	ldy.w #6
	jsl $00A8BF
	rep #$30
	lda $13D3
	ora #$FFE0
	rtl

chart_pick:               ; $00 = grid cell address; out: A 8-bit = the code, M X 8-bit
	sep #$20
	rep #$10
	lda.b #chart_grid>>16
	sta $02
	lda [$00]
	pha
	rep #$20
	lda.w #0
	sta.l !CSUM
	sep #$20
	ldx.w #0
-	lda.l $7FCF6E,x
	cmp #$FF
	beq +
	jsr .add
	inx
	cpx.w #8
	bne -
+	lda 1,s
	jsr .add
	rep #$20
	lda.l !CSUM
	cmp.w #!CAP+1
	sep #$30
	bcs .full
	pla
	rtl
.full:
	pla                   ; the code, then the JSL return: leave like the 7-letter check at $21:E74F
	pla
	pla
	pla
	rep #$30
	jml $219C22
.add:                     ; A 8-bit code -> CSUM += its width (static cells count 8)
	phx
	rep #$20
	and.w #$00FF
	tax
	lda.l vwf_widths,x
	and.w #$00FF
	bne +
	lda.w #8
+	clc
	adc.l !CSUM
	sta.l !CSUM
	sep #$20
	plx
	rts

chart_grid: incbin "../build/vwf/chart.bin"
chart_text: incbin "../build/vwf/chart_text.bin"
assert pc() <= $B0FFFF
