; Battle command buttons in English (docs/re/graphics.md G6, tools/buttons.py). Their tiles sit in the compressed
; block $29:EE12, which $00:8AEE unpacks to $7E:8000 (format not decoded). The unpacker's entry now runs the
; original body as a subroutine, then patches the button tiles when the block just unpacked is that one.

macro btn_copy(dst, len, src)
	ldx #<len>-2
-	lda.l btn_data+<src>,x
	sta.l $7E8000+<dst>,x
	dex
	dex
	bpl -
endmacro

pushpc
org $008AEE               ; was: PHB / SEP #$20 / LDA #$00 (8AF2 = LDA's operand, never reached now)
	jml btn_unpack
pullpc

btn_unpack:
	jsl .body
	php
	rep #$30
	pha
	phx
	ldx #$000E
-	lda.l $7E9100,x       ; tools/buttons.py SIG: the first tile of にげる
	cmp.l btn_sig,x
	bne .out
	dex
	dex
	bpl -
	%btn_copy($0D00, $0040, 0)          ; tools/buttons.py RANGES, packed in buttons.bin in this order
	%btn_copy($0F00, $0040, $0040)
	%btn_copy($1100, $0100, $0080)
	%btn_copy($1300, $0100, $0180)
	%btn_copy($1800, $01C0, $0280)
	%btn_copy($1A00, $01C0, $0440)
.out
	plx
	pla
	plp
	rtl
.body                     ; the replaced instructions, then the original unpacker; its PLB / RTL returns here
	phb
	sep #$20
	lda #$00
	pha
	plb
	jml $008AF5

btn_sig:  incbin "../build/vwf/buttons_sig.bin"
btn_data: incbin "../build/vwf/buttons.bin"
