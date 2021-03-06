
# code

```Ruby
# Test all samples


#category = (ring :ambi, :bass, :bd, :drum, :elec, :guit, :loop, :misc, :perc, :sn, :tabla, :vinyl)
category = sample_groups.sort

# Load samples
puts "Caching samples .."
for idx in 0..category.size-1 do
    puts "  For Category #{category[idx]}"
    sample_names(category[idx]).each do |s|
      puts "    Load #{s} sample"
      load_samples s
    end
  end
  puts ""
  
  # Play samples
  puts "Play samples"
  for idx in 0..category.size-1 do
      with_sample_defaults amp: 4 do
        sample_names(category[idx]).sort.each do |s|
          puts "Play #{category[idx]}-#{s}"
          sample s
          sleep (sample_duration s) + 1
        end
      end
    end
```

#  ambi
    ambi_choir
    ambi_dark_woosh
    ambi_drone
    ambi_glass_hum
    ambi_glass_rub
    ambi_haunted_hum
    ambi_lunar_land
    ambi_piano
    ambi_soft_buzz
    ambi_swoosh
    
![ambi Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_ambi.png)
[ambi Soundcloud](https://soundcloud.com/bruno-adele/test-sample-ambi?in=bruno-adele/sets/sonic-pi-test-samples)
    
  # bass
    bass_dnb_f
    bass_drop_c
    bass_hard_c
    bass_hit_c
    bass_thick_c
    bass_voxy_c
    bass_voxy_hit_c
    bass_woodsy_c

![bass Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_bass.png)
[bass Soundcloud](https://soundcloud.com/bruno-adele/test-sample-bass?in=bruno-adele/sets/sonic-pi-test-samples)

  # bd
    bd_808
    bd_ada
    bd_boom
    bd_fat
    bd_gas
    bd_haus
    bd_klub
    bd_pure
    bd_sone
    bd_tek
    bd_zome
    bd_zum

![bd Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_bd.png)
[bd Soundcloud](https://soundcloud.com/bruno-adele/test-sample-bd?in=bruno-adele/sets/sonic-pi-test-samples)

  # drum
    drum_bass_hard
    drum_bass_soft
    drum_cowbell
    drum_cymbal_closed
    drum_cymbal_hard
    drum_cymbal_open
    drum_cymbal_pedal
    drum_cymbal_soft
    drum_heavy_kick
    drum_roll
    drum_snare_hard
    drum_snare_soft
    drum_splash_hard
    drum_splash_soft
    drum_tom_hi_hard
    drum_tom_hi_soft
    drum_tom_lo_hard
    drum_tom_lo_soft
    drum_tom_mid_hard
    drum_tom_mid_soft

![drum Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_drum.png)
[drum Soundcloud](https://soundcloud.com/bruno-adele/test-sample-drum?in=bruno-adele/sets/sonic-pi-test-samples)

  # elec
    elec_beep
    elec_bell
    elec_blip
    elec_blip2
    elec_blup
    elec_bong
    elec_chime
    elec_cymbal
    elec_filt_snare
    elec_flip
    elec_fuzz_tom
    elec_hi_snare
    elec_hollow_kick
    elec_lo_snare
    elec_mid_snare
    elec_ping
    elec_plip
    elec_pop
    elec_snare
    elec_soft_kick
    elec_tick
    elec_triangle
    elec_twang
    elec_twip
    elec_wood

![elec Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_elec.png)
[elec Soundcloud](https://soundcloud.com/bruno-adele/test-sample-elec?in=bruno-adele/sets/sonic-pi-test-samples)


  # guit
    guit_e_fifths
    guit_e_slide
    guit_em9
    guit_harmonics
    
![guit Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_guit.png)
[guit Soundcloud](https://soundcloud.com/bruno-adele/test-sample-guit?in=bruno-adele/sets/sonic-pi-test-samples)

    
  # loop
    loop_amen
    loop_amen_full
    loop_breakbeat
    loop_compus
    loop_garzul
    loop_industrial
    loop_mika
    loop_safari
    loop_tabla

![loop Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_loop.png)
[loop Soundcloud](https://soundcloud.com/bruno-adele/test-sample-loop?in=bruno-adele/sets/sonic-pi-test-samples)


  # misc
    misc_burp
    misc_cineboom
    misc_crow
    
![misc Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_misc.png)
[misc Soundcloud](https://soundcloud.com/bruno-adele/test-sample-misc?in=bruno-adele/sets/sonic-pi-test-samples)
    
    
  # perc
    perc_bell
    perc_snap
    perc_snap2
    perc_swash
    perc_till

![perc Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_perc.png)
[perc Soundcloud](https://soundcloud.com/bruno-adele/test-sample-perc?in=bruno-adele/sets/sonic-pi-test-samples)


  # sn
    sn_dolf
    sn_dub
    sn_zome
    
![sn Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_sn.png)
 [sn Soundcloud](https://soundcloud.com/bruno-adele/test-sample-sn?in=bruno-adele/sets/sonic-pi-test-samples)
   
    
  # tabla
    tabla_dhec
    tabla_ghe1
    tabla_ghe2
    tabla_ghe3
    tabla_ghe4
    tabla_ghe5
    tabla_ghe6
    tabla_ghe7
    tabla_ghe8
    tabla_ke1
    tabla_ke2
    tabla_ke3
    tabla_na
    tabla_na_o
    tabla_na_s
    tabla_re
    tabla_tas1
    tabla_tas2
    tabla_tas3
    tabla_te1
    tabla_te2
    tabla_te_m
    tabla_te_ne
    tabla_tun1
    tabla_tun2
    tabla_tun3

![tabla Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_tabla.png)
[tabla Soundcloud](https://soundcloud.com/bruno-adele/test-sample-tabla?in=bruno-adele/sets/sonic-pi-test-samples)


  # vinyl
    vinyl_backspin
    vinyl_hiss
    vinyl_rewind
    vinyl_scratch

![vinyl Screenshot](https://raw.githubusercontent.com/badele/sonic-pi-tools/master/test/sample/test_sample_vinyl.png)
[vinyl Soundcloud](https://soundcloud.com/bruno-adele/test-sample-vinyl?in=bruno-adele/sets/sonic-pi-test-samples)
