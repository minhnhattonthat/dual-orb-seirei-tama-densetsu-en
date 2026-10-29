; Controller screen (Config > Controller > Custom, $21:DDC8). The game unpacks one of six stored BG3 tilemaps (per
; mode $1424, table $21:DE82) to $7E:8000 every frame and DMAs it to VRAM $7800; its labels (rows 3-8: header,
; A-D / right-hand / left-hand modes) are kana glyph tiles, now VWF pool tiles, so junk (issue #1). The mode cursor
; is a sprite pair. Now the labels are printed once in English into the BG3 buffer rows 3-8 on entry, and every
; unpack takes those rows from the buffer.

!CROW = ($C0)             ; first label row (3), byte offset in a 32-cell tilemap
!CLEN = ($180)            ; rows 3-8

pushpc
org $21DDE0               ; entry: was JSL $00D943 (tilemap | $2000); then MVN $7E:8000 -> $7F:F000, DMA
	jsl ctl_enter
org $21DE4C               ; every frame: same unpack, DMA'd straight from $7E:8000
	jsl ctl_frame
pullpc

ctl_enter:
	jsl $00D943
	rep #$30
	lda.w #$216A              ; the stored tilemap's blank cell
	ldx.w #!CLEN-2
-	sta.l $7FF000+!CROW,x
	dex
	dex
	bpl -
	lda.w #ctl_text
	sta $B3
	lda.w #ctl_text>>16
	sta $B5
	ldx.w #$0000
	ldy.w #$0000
	jsl $00A8BF
	bra +
ctl_frame:
	jsl $00D943
+	php
	rep #$30
	ldx.w #!CLEN-2
-	lda.l $7FF000+!CROW,x
	sta.l $7E8000+!CROW,x
	dex
	dex
	bpl -
	plp
	rtl

ctl_text:                 ; {pos x,y} + text (tbl/en.tbl); x/y from the kana labels' cells
	db $F4,$04,$03,$0C,$4F,$4E,$54,$52,$4F,$4C,$4C,$45,$52,$31          ; Controller:
	db $F4,$05,$05,$0A,$40,$16,$4F,$44,$45                              ; A Mode
	db $F4,$0D,$05,$0C,$40,$16,$4F,$44,$45                              ; C Mode
	db $F4,$15,$05,$1B,$49,$47,$48,$54,$32,$11,$41,$4E,$44              ; Right-Hand (ends x 224)
	db $F4,$05,$07,$0B,$40,$16,$4F,$44,$45                              ; B Mode
	db $F4,$0D,$07,$0D,$40,$16,$4F,$44,$45                              ; D Mode
	db $F4,$15,$07,$15,$45,$46,$54,$32,$11,$41,$4E,$44,$FF              ; Left-Hand
