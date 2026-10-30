; Controller screen (Config > Controller > Custom, $21:DDC8). The game unpacks one of six stored BG3 tilemaps (per
; mode $1424, table $21:DE82) to $7E:8000 every frame and DMAs it to VRAM $7800; its labels (rows 3-8: header,
; A-D / right-hand / left-hand modes) are kana glyph tiles, now VWF pool tiles, so junk (issue #1). The mode cursor
; is a sprite pair. Now the labels are printed once in English into the BG3 buffer rows 3-8 on entry, and every
; unpack takes those rows from the buffer.

; The "O.K." / "CANCEL" labels move with the mode (rows 9-27) and use the font's latin glyph tiles, also pool tiles,
; so junk once other text has run (#3). They are printed into the hidden rows 28-29 on entry and pasted over each
; unpack's label cells, found by their first tile (O $028, C $00C).

!CROW = ($C0)             ; first label row (3), byte offset in a 32-cell tilemap
!CLEN = ($180)            ; rows 3-8
!LROW = ($700)            ; row 28: O.K. at cols 0-3, CANCEL at cols 8-13 (row 29 = bottom halves)
!POK = $7FF000+$780       ; label offsets found this frame (row 30, never shown: the entry's MVN overwrites it)
!PCN = $7FF000+$782

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
	ldx.w #$007E
-	sta.l $7FF000+!LROW,x
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
	ldx.w #$007E              ; rows 28-29 too, so the entry's MVN back into the buffer keeps them (off screen)
-	lda.l $7FF000+!LROW,x
	sta.l $7E8000+!LROW,x
	dex
	dex
	bpl -
	lda.w #$FFFF              ; find both labels first, so a pasted pool tile is never taken for a label
	sta.l !POK
	sta.l !PCN
	ldx.w #!CROW+!CLEN        ; rows 9-27
-	lda.l $7E8000,x
	and.w #$03FF
	cmp.w #$0028
	bne +
	txa
	sta.l !POK
	bra ++
+	cmp.w #$000C
	bne ++
	lda.l !PCN
	bpl ++                    ; keep the first C (the label's second C is further right)
	txa
	sta.l !PCN
++	inx
	inx
	cpx.w #!LROW
	bcc -
	lda.l !POK
	bmi +
	tax
	ldy.w #$0000              ; O.K.: buffer cols 0-3
	lda.w #$0008
	jsr ctl_paste
+	lda.l !PCN
	bmi +
	tax
	ldy.w #$0010              ; CANCEL: buffer cols 8-13
	lda.w #$000C
	jsr ctl_paste
+	plp
	rtl

ctl_paste:                ; X = label's top-left offset in $7E:8000, Y = offset in the buffer's row 28, A = bytes
	pei ($00)                 ; $00/$04/$06 hold the game's DMA size/source
	pei ($02)
	pei ($04)
	pei ($06)
	sta $06
	txa
	clc
	adc.w #$8000
	sta $00                   ; [$00] = $7E:8000 + X
	tya
	clc
	adc.w #$F000+!LROW
	sta $03                   ; [$03] = $7F:F000 + row 28 + Y
	sep #$20
	lda.b #$7E
	sta $02
	lda.b #$7F
	sta $05
	rep #$20
	ldy.w #$0000
-	lda [$03],y
	sta [$00],y
	tya
	clc
	adc.w #$0040
	tay
	lda [$03],y               ; bottom half, one row down
	sta [$00],y
	tya
	sec
	sbc.w #$003E
	tay
	cpy $06
	bcc -
	pla
	sta $06
	pla
	sta $04
	pla
	sta $02
	pla
	sta $00
	rts

ctl_text:                 ; {pos x,y} + text (tbl/en.tbl); x/y from the kana labels' cells
	db $F4,$04,$03,$0C,$4F,$4E,$54,$52,$4F,$4C,$4C,$45,$52,$31          ; Controller:
	db $F4,$05,$05,$0A,$40,$16,$4F,$44,$45                              ; A Mode
	db $F4,$0D,$05,$0C,$40,$16,$4F,$44,$45                              ; C Mode
	db $F4,$15,$05,$1B,$49,$47,$48,$54,$32,$11,$41,$4E,$44              ; Right-Hand (ends x 224)
	db $F4,$05,$07,$0B,$40,$16,$4F,$44,$45                              ; B Mode
	db $F4,$0D,$07,$0D,$40,$16,$4F,$44,$45                              ; D Mode
	db $F4,$15,$07,$15,$45,$46,$54,$32,$11,$41,$4E,$44                  ; Left-Hand
	db $F4,$00,$1C,$18,$37,$14,$37                                      ; O.K. (row 28)
	db $F4,$08,$1C,$0C,$0A,$17,$0C,$0E,$15,$FF                          ; CANCEL
