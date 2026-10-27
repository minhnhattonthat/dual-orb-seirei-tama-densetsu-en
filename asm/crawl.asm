; Intro crawl ($0C:D3E9 loop, docs/re/text.md §Intro crawl). The game prints each page (16 lines) whole into one half
; of the BG3 map at once. An English page needs 183-260 VWF cells and the pool holds 182, so a page's first lines were
; overwritten by its last ones. Now a page is only queued; each loop pass prints its next line once that line nears the
; screen bottom, and blanks the map row passing above the window so the sweep can free the cells it showed.

!CPTR   = $7FEEF0         ; next line of the page (24-bit)
!CROW   = $7FEEF4         ; its BG3 map row (8 px rows, 0-63)
!CDONE  = $7FEEF6         ; nonzero once the page's FF is read
!LBUF   = $7FEE80         ; the line, FF-terminated, as the printer's text
!SCROLL = $0D9C           ; BG3 V-scroll (NMI writes it to $2112)
!DIRTY  = $0A67           ; word per BG3 map row; DEC = upload the row

pushpc                    ; the code goes after asm/namechart.asm's data in bank $B0
org $0CD673               ; was: cmd 1 -> JSR $D69E (clear the half), print page $24 at row $22 through $00:A8BF
	lda $20
	cmp.w #$0001
	bne +
	jsr $D69E
	lda $24
	asl
	tax
	lda $D696,x
	jsl crawl_page
+	jsl crawl_tick
	rts
assert pc() <= $0CD696    ; the page pointer table
pullpc

crawl_page:               ; A = page address in bank $0C, M/X 16, DB = $0C
	sta $00
	lda.w #$000C
	sta $02
	lda [$00]
	and.w #$00FF
	cmp.w #$00DF              ; {jump} stub (asm/names.asm): the page is in bank $3E
	bne +
	ldy.w #2
	lda [$00],y               ; hi, bank
	tax
	dey
	lda [$00],y               ; lo, hi
	sta $00
	txa
	xba
	and.w #$00FF
	sta $02
+	lda $00
	sta.l !CPTR
	lda $02
	sta.l !CPTR+2
	lda $22
	sta.l !CROW
	lda.w #$0000
	sta.l !CDONE
	lda $22                   ; upload the cleared half, as the whole-page print did (its 32-row box)
	asl
	tax
	ldy.w #32
-	dec !DIRTY,x
	inx
	inx
	dey
	bne -
	rtl

crawl_tick:               ; every loop pass, M/X 16, DB = $0C
	lda.l !CDONE
	bne .blank
	lda.l !CROW               ; screen y of the next line = row*8 - scroll (mod 512)
	asl
	asl
	asl
	sec
	sbc !SCROLL
	and.w #$01FF
	cmp.w #240                ; just below the screen: print it now
	bcc .line
	cmp.w #448                ; above the top (late): print it anyway
	bcc .blank
.line:
	jsr crawl_line
.blank:                   ; the row at screen y 64-71, above the crawl window (it starts at y ~96)
	lda !SCROLL
	clc
	adc.w #64
	lsr
	lsr
	lsr
	and.w #$003F
	sta $04
	asl
	asl
	asl
	asl
	asl
	asl
	tax
	stz $06
	ldy.w #32
-	lda.l $7FF000,x
	cmp.w #$216A              ; the blank cell
	beq +
	lda.w #$216A
	sta.l $7FF000,x
	inc $06
+	inx
	inx
	dey
	bne -
	lda $06
	beq +
	lda $04
	asl
	tax
	dec !DIRTY,x
+	rtl

crawl_line:               ; copy the next line to !LBUF and print it at column 4, row !CROW
	lda.l !CPTR
	sta $00
	lda.l !CPTR+1
	sta $01
	sep #$20
	ldy.w #0
-	lda [$00],y
	cmp #$FD                  ; {n}
	beq .eol
	cmp #$FF
	beq .eop
	tyx
	sta.l !LBUF,x
	iny
	bra -
.eop:
	lda #$01
	sta.l !CDONE
.eol:
	tyx
	lda #$FF
	sta.l !LBUF,x
	rep #$20
	iny
	tya
	clc
	adc.l !CPTR
	sta.l !CPTR
	lda.l !CROW
	pha
	inc
	inc
	and.w #$003F
	sta.l !CROW
	ply
	lda.l !LBUF
	and.w #$00FF
	cmp.w #$00FF
	beq +
	lda.w #!LBUF                ; A8BF's setup with a 2-row box: it marks the box rows dirty (32 would pass row 63)
	sta $B3
	lda.w #!LBUF>>16
	sta $B5
	lda.w #$0004
	sta $0E03
	sty $0E07
	lda.w #$0020
	sta $0E05
	lda.w #$0002
	sta $0E09
	stz $0DFB
	stz $0DFF
	jsl $00A89E
	jsl $00A8E3
+	rts
assert pc() <= $B0FFFF
