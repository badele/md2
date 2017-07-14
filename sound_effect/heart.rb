live_loop :heart do
        with_sample_defaults amp: 6 do
            sample :bd_808, beat_stretch: 0.25, rate: -1, finish: 0.3
            sleep rrand(0.25, 0.3)
            sample :bd_808, beat_stretch: 0.25, rate: -1, finish: 0.3
            sleep rrand(0.6, 0.7)
        end
end
