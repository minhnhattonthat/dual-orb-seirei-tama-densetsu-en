; Compass screen (field menu "Compass", $21:9C81). The game unpacks a stored BG3 tilemap ($2A:C03C -> $7E:8000) whose
; eight direction labels are kana glyph tiles (now VWF pool tiles, so junk) and DMAs it to VRAM $7C00, the map's
; bottom half. Now the tilemap goes into the BG3 buffer's bottom half ($7F:F800, which the game cleared for it), the
; label cells are blanked and English labels printed there through the text engine, and the DMA reads the buffer.

!CBUF = $7FF800           ; BG3 buffer, map rows 32-63

pushpc
org $219CF7               ; was: JSL $00D943 (tilemap | $2000), then $00/$04/$06 = size/source for the DMA at 9D02
	jsl compass_draw
pullpc

compass_draw:
	jsl $00D943
	rep #$30
	ldx.w #$07FE
-	lda.l $7E8000,x
	sta.l !CBUF,x
	dex
	dex
	bpl -
	lda.w #$216A              ; the stored tilemap's blank cell
	ldx.w #$007E              ; (asar math runs left to right: offsets are bracketed)
-	sta.l !CBUF+(2*$40),x     ; rows 2-3 (NW, N, NE) and 24-25 (SW, S, SE): labels only
	sta.l !CBUF+(24*$40),x
	dex
	dex
	bpl -
	ldx.w #$000A
-	sta.l !CBUF+(13*$40),x    ; rows 13-14: W at cols 0-5, E at cols 26-31 (the arrow is cols 6-25)
	sta.l !CBUF+(14*$40),x
	sta.l !CBUF+(13*$40+52),x
	sta.l !CBUF+(14*$40+52),x
	dex
	dex
	bpl -
	lda.w #compass_text
	sta $B3
	lda.w #compass_text>>16
	sta $B5
	stz $0E03                 ; A8BF's setup with a box of rows 32-57 (a 32-row box would pass row 63)
	lda.w #$0020
	sta $0E07
	sta $0E05
	lda.w #$001A
	sta $0E09
	stz $0DFB
	stz $0DFF
	jsl $00A89E
	jsl $00A8E3
	rep #$30
	lda.w #$0800              ; DMA 2 KB from the buffer instead of $7E:8000
	sta $00
	lda.w #!CBUF
	sta $04
	lda.w #!CBUF>>16
	sta $06
	rtl

compass_text:             ; {pos x,y} + text (tbl/en.tbl); x from the kana labels' cells, y = 32 + their row
	db $F4,$02,$22,$17,$4F,$52,$54,$48,$57,$45,$53,$54          ; Northwest
	db $F4,$0E,$22,$17,$4F,$52,$54,$48                          ; North
	db $F4,$17,$22,$17,$4F,$52,$54,$48,$45,$41,$53,$54          ; Northeast (ends x 236)
	db $F4,$02,$2D,$20,$45,$53,$54                              ; West
	db $F4,$1B,$2D,$0E,$41,$53,$54                              ; East
	db $F4,$02,$38,$1C,$4F,$55,$54,$48,$57,$45,$53,$54          ; Southwest
	db $F4,$0E,$38,$1C,$4F,$55,$54,$48                          ; South
	db $F4,$17,$38,$1C,$4F,$55,$54,$48,$45,$41,$53,$54,$FF      ; Southeast
