; Field item menu: the prompt box and the info panel become one full-width window (x8 w240) so the item name gets
; 88 px (col $13, after the icon frame at col $10) and the description 224 px on its own row (col 2).
; Window records (bank $21): x, y, w, h words, then style words.

org $21BF4F               ; prompt box x16 y8 w96 h32 -> the panel's rectangle (drawn as one window)
	dw $0008,$0008,$00F0,$0038
; Field menu (Magic .. Compass): window, text and left cursor bracket 8 px left, so "Compass" (45 px) ends before the
; right bracket, which sits at a fixed x $F2 ($21:94CE)
org $2192F0               ; window record x192 w56 -> x184 w64
	dw $00B8
org $2192F4
	dw $0040
org $21935A               ; LDX #$0019: text column 25 -> 24
	db $18
org $2194AB               ; LDA #$00C6: left bracket x -> $BE
	db $BE
org $1084C7              ; place-name label ($10:8486, text from x16): w80 -> 136 for the longest name (119 px)
	dw $0088                ; shortcut: one width for every name; size it to the name if short ones look boxed-in
org $21BF82               ; info panel x120 w120 -> x8 w240
	dw $0008
org $21BF86
	dw $00F0

org $21B568               ; icon sprite centre x 140 -> 132 and its frame col $10 -> $0F (8 px gap before the name;
	dw $0084                  ; the prompt "Which will you use?" moved to col 2 in script/system.json 21:C04F)
org $21B5F1
	db $0F
org $21B8FF               ; same x when the chosen item's icon moves to sprite slot 0 (use on whom / town)
	dw $0084
org $21BCB4
	dw $0084

org $21B990               ; prompts in the same row: col 3 -> 2 (LDX #$0003): "Use it on whom?" (21:C08D)
	db $02
org $21B91D               ; ... and the 12-cell blank 21:C098 that clears the prompt
	db $02
org $21BACE
	db $02
org $21BDC5
	db $02

org $21B60C             ; underlines ($01:8000 list: length, column, row): name 8 @ $15 -> 11 @ $13,
	db $0B,$13,$04            ; description 13 @ $10 -> 28 @ 2
	db $1C,$02,$07

; Name and description strings at $028C (was 8 / 13 blanks, then F6 n back, then the text); called by JSR at $21:B5B2.
!IPNAME = 11
!IPDESC = 28
org $21B614
	sep #$30
	ldx.b #!IPNAME-1
	jsr ipanel_blanks
	lda #$F6
	sta.w $028C+!IPNAME
	lda.b #!IPNAME
	sta.w $028C+!IPNAME+1
	lda #$E5                  ; item name table
	sta.w $028C+!IPNAME+2
	lda $13C3
	asl a
	tax
	lda $1121,x
	bne +
	lda #$FF                  ; empty slot: blanks only
	sta.w $028C+!IPNAME+2
+	sta.w $028C+!IPNAME+3
	lda #$FF
	sta.w $028C+!IPNAME+4
	rep #$30
	ldx #$0013
	ldy #$0002
	jsr ipanel_draw
	sep #$30
	ldx.b #!IPDESC-1
	jsr ipanel_blanks
	lda #$F6
	sta.w $028C+!IPDESC
	lda.b #!IPDESC
	sta.w $028C+!IPDESC+1
	lda #$3C                  ; description dictionary
	sta.w $028C+!IPDESC+2
	lda #$FF
	sta.w $028C+!IPDESC+5
	rep #$30
	lda $13C3
	asl a
	tax
	lda $1121,x
	bne +
	lda #$FFFF                ; empty slot: blanks only
	sta.w $028C+!IPDESC
+	sta.w $028C+!IPDESC+3
	ldx #$0002
	ldy #$0005
	jsr ipanel_draw
	bra ipanel_done
ipanel_blanks:            ; X+1 cell spaces at $028C (A, X 8-bit)
	lda #$3F
-	sta $028C,x
	dex
	bpl -
	rts
ipanel_draw:              ; print $00:028C at column X, row Y
	stz $0E33
	stz $0E35
	lda #$028C
	sta $B3
	stz $B5
	jsl $00A8BF
	rts
	warnpc $21B6E0
	padbyte $EA : pad $21B6E0
ipanel_done:
assert ipanel_done == $21B6E0

; Field magic menu: the info panel (record $21:B324, h80; $21:B330 is its h56 twin) widens one cell left,
; x120 w120 -> x112 w136 (it now meets the caster box at x112); description and the MP-cost underline start at
; col $0F: 15 cells = 120 px (was 13 = 104). Name (col $15, 64 px) and "MP cost:" (col $14) stay.
org $21B324
	dw $0070
org $21B328
	dw $0088
org $21B330
	dw $0070
org $21B334
	dw $0088
org $21A22F               ; underlines ($21:A22C list): name 8 @ $15 row 4 kept; rows 7 and 10: 13 @ $10 -> 15 @ $0F
	db $0F,$0F,$07
	db $0F,$0F,$0A

!MPDESC = 15
org $21A375               ; description string at $028C, drawn at col $10 -> $0F (the name part before it is kept)
	sep #$30
	ldx.b #!MPDESC-1
	jsr ipanel_blanks
	lda #$F6
	sta.w $028C+!MPDESC
	lda.b #!MPDESC
	sta.w $028C+!MPDESC+1
	lda #$3C
	sta.w $028C+!MPDESC+2
	lda #$FF
	sta.w $028C+!MPDESC+5
	rep #$30
	lda $13BF
	asl a
	tax
	lda $1121,x
	bne +
	lda #$FFFF                ; empty slot: blanks only
	sta.w $028C+!MPDESC
+	sta.w $028C+!MPDESC+3
	ldx #$000F
	ldy #$0005
	jsr ipanel_draw
	warnpc $21A3E3
	padbyte $EA : pad $21A3E3

; Town picker (Telepiam / "Go to which town?", list builder $21:AD26): 3 columns x 2 rows of 72 px -> 2 columns x
; 2 rows (cols 3 and 16, 104 px each; town names up to 81 px). Index = row * 3 + col + scroll ($7FCF48/46/CEEE).
org $21ACF3 : db $EA,$EA,$EA,$EA,$EA  ; row * 3 -> row * 2 (drop the ADC row after the ASL): pick, cursor, confirm
org $21AE90 : db $EA,$EA,$EA,$EA,$EA
org $21AEC0 : db $EA,$EA,$EA,$EA,$EA
org $21BD7C : db $EA,$EA,$EA,$EA,$EA
org $21ADEF : db $02      ; scroll by one row: 3 -> 2
org $21AE30 : db $02
org $21AE22 : db $04      ; a page holds 6 -> 4 (scroll-down limit, down arrow)
org $21AFCB : db $04
org $21AF27 : db $04      ; names drawn per page
org $21AE50 : db $01      ; rightmost column 2 -> 1
org $21AF6B               ; name cells (col, row) per slot
	dw 3,16,3,16
org $21AF77
	dw 19,19,22,22
org $21AEEE               ; cursor bracket x, y per slot; right bracket at x + $44 -> + $58
	dw $14,$7C,$14,$7C        ; 2 px further left than the JP $16 (VWF text starts at the cell edge)
org $21AEFA
	dw $A0,$A0,$B8,$B8
org $21AED1 : dw $0058
; info line {name}:{desc} at $0200: the code-written colon ($31) -> $60 "：" = colon + word space (fonts/vwf.txt)
org $01A002 : db $60
org $01AEA5 : db $60
org $01BC6B : db $60
org $21CFBA : db $60      ; equip menu: the same line from a template MVN-copied to $028C ($21:CA6F)
