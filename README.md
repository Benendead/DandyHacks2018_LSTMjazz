# Summary
*This document is a work-in-progress of summarizing what has been and what remains to be done.*

Last revised 12/25/2019.

Project started at the DandyHacks 2018 hackathon in October 2018, continued into summer 2019, and hopefully to be completed winter break 2019. It's been on-and-off but I'd like to get this done.

## Overall Goal
Train an LSTM model to improvise over jazz chord sequences. Such a system could be used in live setting for jam sessions or provide practice material in a sightreading application.

## Previous Approaches

Choi et al. (2016) - Used char-RNN and word-RNN to create a chord sequence generator. Their data came from 2,486 scores transposed to C from real books and was encoded using simple text data, e.g. -START- F:9 F:9 F:9 F:9 D:min7 D:min7 G:9 G:9 C:maj C:maj ... There were 39 distinct characters, 1,259 distinct chords, and 539,609 chords overall. Char-RNN allowed a smaller vocabulary and fewer assumptions to made about the music, but its effective length of memory is constrained because passing data into the model just takes longer. Their model learned ii-V-I, passing chords, tritone subs, and modal interchange, among other jazz idioms.

**Write up rest as well**

Here's a summary of the previous approaches I looked at:

---
Author(s) | Year | Models Used | Music | Encoding | Quantization | Future work | Code/Examples
--- | --- | --- | --- | --- | --- | --- | ---
Eck | 2002 | LSTM | Melody + chords | 13 melody, 12 chord 1/0 | 2 per beat | N/A | [Ex](https://web.archive.org/web/20190104192500/http://people.idsia.ch/~juergen/blues/)
Bickerman | 2010 | DBN | Chords -> jazz licks | 18 melody (12 pitch, 4 8va), 12 chord | 12 per beat | Melodies avoid triplets | [Code](https://sourceforge.net/projects/rbm-provisor/)
Choi | 2016 | char-RNN, word-RNN | Jazz chord progressions | Note chars, Chord words | 1 per beat | N/A | [Code](https://github.com/keunwoochoi/lstm_real_book) [Blog](https://keunwoochoi.wordpress.com/2016/02/19/lstm-realbook/)
Lackner | 2016 | LSTM | Melody given chords | 24 melody, 12 chord 1/0 | 4 per beat | Larger dataset | [Ex](https://konstilackner.github.io/LSTM-RNN-Melody-Composer-Website/)
Agarwala | 2017 | Seq2Seq, char-RNN | Melodies | ABC char -> embeddings | None; ABC notation | N/A | [Code](https://github.com/yinoue93/CS224N_proj)
Brunner | 2017 | 2 LSTMs | Chords -> polyphonic piano | 48 melody, 50 chord embeddings | 2 per beat | Encoding polyphonic sustain, genre metadata | N/A
Hilscher | 2018 | char-RNN | Polyphonic piano | 1/0 on/off vectors | 4 per beat | More keys/data, text pattern matching | [Ex](https://yellow-ray.de/~moritz/midi_rnn/examples.html)

## Data Pipeline

*Dataset* - I started with MIDI versions of 50 songs from the Charlie Parker omnibook. These were provided on Ken Déguernel's site. The songs had a mean length of 281.68 beats and median of 260.

*Transposition* - With this MIDI data, I used music21 to create 12 copies of each song in all 12 keys. This gives 600 total songs, which have 169008 beats of data overall. Even after this transposition, there were only 84 unique chords present in the data. I processed the chords into bit vectors as well as tokens.

*Melody Encoding* - We also have to consider how many notes the system should be allowed to play; the original 50 songs had a range of 32 MIDI notes, between D3 and A5, but the transposed dataset spans 43 notes now up to G#6. This could only be reduced to 42 notes, so I've left the dataset with a range from C#3 to F#6. Two encoding formats for melody were output:

1. A piano roll encoding using 42 on/off bits. (seems naive)
2. An 18-bit representation using 12 columns for the 12 notes, four for octave options 3 to 6, and then two more bits for sustain and rest.

Another option might be just the 16 bits of notes + octave, we'll see if that's worth looking into. **TO DO**

Each of these data formats was then output to .csv files.


## Training an LSTM

We have a sequence of chords and a corresponding melody. For an LSTM to predict some timestep of melody given chords, it needs a window of the previous chord data. Thus the encoded chord data needs to be sampled into some windows of length t; each sample is labeled by the melody data at the t+1 timestep. The final shape of the chord data will be a 3D matrix of dimensions: # samples, time steps per sample, chord encoding dimension.

*LSTM structure* - The actual network has a lot of options to consider. For each combination of melody and chord encodings, the network topology necessarily changes. Thus I'd better pick a combination to start with: chord bit vectors and the 18-bit melody encoding have the lowest dimensionality.

Looking over previous work, the Lackner and Agarwala networks seem to have the input and output dimensionalities most similar to this, and they found success in 12-9-18-24 units per layer or 20-800, respectively. Agarwala notes that the char-RNN did better with smaller embedding sizes whereas the Seq2Seq model preferred larger embedding sizes. Both benefitted from a large hidden state size.

With this in mind, I'll start with a simple network and probably work my way up to larger sizes once the training infrastructure is consistent/easy to get started. The very first model, after over a year of on-and-off work, will take the 12-bit vectors, go through two 18-unit layers, and output to the 18-bit melody representation.

I'll start from scratch in a new notebook and go from there.

## Implementation Notes

*Time resolution* - I'd like my system to have 12 timesteps per beat. This allows 16th notes as well as 8th-note triplets.

```
1|||||||||||2|||||||||||3|||||||||||4|||||||||||1
1  e  +  a  2  e  +  a  3  e  +  a  4  e  +  a  1
1   t   t   2   t   t   3   t   t   4   t   t   1
1||et|+|ta||2||et|+|ta||3||et|+|ta||4||et|+|ta||1
```

All of these subdivisions aren't actually used. The bottom line here illustrates this. Only six of the twelve timesteps actually contain an 'identifiable' subdivision of the beat; half of them don't have an typical use in most music playing. For now I'll leave all 12 equal divisions in, but this could probably be optimized. **TO DO**

*Chord sample length* - To start, I chose 96 time steps per sample. This is 12 steps per beat * 4 beats per measure * 2 measures = 96. This gives the model a reasonable idea of what's come before in order to play its next note. There's also the question of *how often* the samples should be taken; training the LSTM on all 12 possible timesteps for each song might cause training to take prohibitively long. We'll see what the damage is over the next week. **TO DO**

*Additional features* - In the work of Brunner et al. (2017), their polyphonic melody generator received piano roll vectors of both the current chord and the next chord. They also include a binary counter from 0 to 7 which gives the system a sense of where it is within the measure. For now, I'd like to get my system working at all and from there may add features like these. **TO DO**

**TLDR of decisions made**

* Timesteps per beat: 12.
* Timesteps per chord sample: 96.
* Sample frequency: Every timestep.
* Additional features: None included.

## NOTEBOOKS READ
As I come back to this project after months of focusing on school, I've actually needed to read up on what I'd already completed. Here's the notebooks I've covered so far:

* Data Preprocessing
* Final Preprocessing started but clearly something else comes first
* Summaries started but I get what's relevant

## Citations (very incomplete)
Using Multidimensional Sequences For Improvisation In The OMax Paradigm
Ken Déguernel, Emmanuel Vincent, Gérard Assayag
13th Sound and Music Computing Conference, Aug 2016, Hamburg, Germany. 〈http://quintetnet.hfmt-hamburg.de/SMC2016/〉
