; Names relocated (phase 7): the strings of the E4-F9 and 3C tables live in bank $3F (tools/insert.py writes them
; and the pointer arrays, which stay at their bank $00 addresses). Inserted strings are copied into a 256-byte
; buffer at $7F:EF00 instead of the 32-byte $0E11 (English names and shop phrases run past 31 bytes).
; Sites verified against the original bytes by tests/test_vwf.py (test_names_hook_sites_match_original). docs/re/text.md §Names relocated.

!NAMEBANK = $3F
!NBUF     = $7FEF00

macro tablehandler(lda)   ; LDA $tbl,x / STA $00 / SEP #$20 / LDY #0 / LDA ($00),y / STA $0E11,y
	org <lda>+3
	jsr names_setp
	nop
	org <lda>+10
	lda [$00],y
	jsr names_wby
endmacro

%tablehandler($00AB62)    ; E4
%tablehandler($00AB94)    ; F2
%tablehandler($00ABC6)    ; E5
%tablehandler($00ABF8)    ; E6
%tablehandler($00AC2A)    ; E7
%tablehandler($00AC5C)    ; E8
%tablehandler($00AC8E)    ; E9
%tablehandler($00ACC0)    ; EA
%tablehandler($00ACF2)    ; EB
%tablehandler($00AD24)    ; F3
%tablehandler($00AD56)    ; EC
%tablehandler($00AD88)    ; ED
%tablehandler($00ADBA)    ; F9

org $00AA3F               ; 3C: STA $02 / SEP #$20 -> string pointer into $00, bank in $02
	jsr names_setp
	nop
org $00AA46
	lda [$00],y
	jsr names_wby

org $00AA83               ; F0 yes/no
	jsr names_wbx
org $00AAC0               ; EE
	jsr names_wbx
org $00AAFC               ; EF
	jsr names_wbx
org $00AB3E               ; E0-E3 party names
	jsr names_wbx

org $00AF35               ; buffer readers (A, X, Y 16-bit)
	jsr names_rby
org $00AF41
	jsr names_rby
org $00AF60
	jsr names_rby

org $20A50F               ; battle panel, third field (weapon/spell/item/skill name): column $17 -> $14, 88 px
	db $14                    ; (LDX #$0017 at $20:A50E; the command field before it keeps 40 px)

org $21F28D               ; save confirm (21:F755) cursor sprite x: left Yes/No, right Yes/No (was B5 CE CA EB)
	db $B5,$D4,$CE,$E8       ; brackets round "Yes" at x=184 and "No" at 216 (one `_` cell between)

org $21F29E               ; file select "New Game" (52 px): text column $0D -> $0C (LDX #$000D at $21:F29D)
	db $0C
org $21F2CD               ; ... and its window x 100 -> 88, width 48 -> 64 (y 20, h 24 kept)
	db $58,$00,$14,$00,$40
org $21F1A1               ; ... and its cursor corners (x of TL TR BL BR, table per slot) 104/144 -> 92/148
	db $5C,$94,$5C,$94

org $00A98F             ; glyph path of the interpreter (A 8-bit, Y = $0DF9): code DF = jump
	jsr names_glyph

org $00D680               ; freed: name strings no longer live in bank $00 (after the 3C9 pointer array)
names_setp:
	sta $00
	sep #$20
	lda #!NAMEBANK
	sta $02
	rts
names_wby:
	phx
	tyx
	sta.l !NBUF,x
	plx
	rts
names_wbx:
	sta.l !NBUF,x
	rts
names_rby:
	phx
	tyx
	lda.l !NBUF,x
	plx
	rts
; {jump:XXXXXX} (DF lo hi bank): the string goes on at that 24-bit address. Over-long system text keeps a 4-byte
; stub in place and is written whole to a free bank (tools/insert.py).
!JUMP = $DF
names_glyph:
	cmp #!JUMP
	beq .jump
	jmp $AEB6
.jump:
	rep #$30
	pla                       ; drop the return to $A992 (INC $0DF9)
	iny
	lda [$B3],y               ; lo, hi
	tax
	iny
	iny
	sep #$20
	lda [$B3],y               ; bank
	sta $B5
	rep #$20
	stx $B3
	stz $0DF9
	jmp $A94C
assert pc() <= $00D753
