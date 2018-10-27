#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##    ## ##    ## ##    ##
######## ######## ########
###   Ken  Deguernel   ###
######## ######## ########
###   Inria  (Nancy)   ###
###   Ircam  (Paris)   ###
######## ######## ########



######## IMPORTS ########
import xml.etree.ElementTree as ET

######## CLASSES ########

######## XmlScore
# def __init__(self, divisions, beats, beat_type, key)
########
class XmlScore:
	def __init__(self, divisions, beats, beat_type, key):
		self.divisions = divisions		# number of division (based on tatum) in a quarter note
		self.beats = beats				# time signature numerator
		self.beat_type = beat_type		# time signature denominator
		self.key = key					# number of flats or sharps (negative for flats, positive for sharps)



######## XmlNote
# def __init__(self, step, alter, octave, duration)
# def addTimestamp(self, timestamp)
# def changeDuration(self, new_duration)
########
class XmlNote:
	def __init__(self, step, alter, octave, duration):
		self.step = step				# name of the note (without alteration)
		self.alter = alter				# alteration of the note (negative for flats, positive for sharps)
		self.octave = octave			# number of the octave (4 for the octave starting with middle C)
		self.duration = duration		# duration of the note in division (see corresponding XmlScore)
		self.timestamp = None			# timestamp of the note's attack in division

	def addTimestamp(self, timestamp):
		self.timestamp = timestamp

	def changeDuration(self, new_duration):
		self.duration = new_duration



######## XmlChord
# def __init__(self, step, alter, kind)
# def addDuration(self, duration)
# def addTimestamp(self, timestamp)
########
class XmlChord:
	def __init__(self, step, alter, kind):
		self.step = step				# name of the root (without alteration) of the chord
		self.alter = alter				# alteration of the root of the chord (negative for flats, positive for sharps)
		self.kind = kind				# kind of the chord (major, minor, dominant...)
		self.duration = None			# duration of the chord in diviion (see corresponding XmlScore)
		self.timestamp = None			# timestamp of the chord's attack in division

	def addDuration(self, duration):
		self.duration = duration

	def addTimestamp(self, timestamp):
		self.timestamp = timestamp



######## FUNCTIONS ########
def xml_parser(file_name):
	print "PARSING FILE : ", file_name
	tree = ET.parse(file_name)
	root = tree.getroot()

	# Score attributes
	divisions = None
	beats = None
	beat_type = None
	key = None

	# Chords attributes
	chord_root_step = None
	chord_root_alter = None
	chord_kind = None
	chord_duration = None
	chord_timestamp = None

	# Notes attributes
	note_step = None
	note_alter = None
	note_octave = None
	note_duration = None
	note_timestamp = None

	# List of chords and notes
	chord_list = []
	note_list = []

	global_clock = 0			# initialise clock to 0
	global_tied = 0				# boolean to create only one note when there are tied notes

	measures = root.find("part").getchildren()		# returns list of measures (bars)

	for measure in measures:
		for event in measure:		# each event can correspond to a score, note, or chord attribute
			# getting score attributes
			if event.tag == "attributes":
				if event.find("divisions") != None:
					divisions = int(event.findtext("divisions"))
				if event.find("time") != None:
					beats = int(event.find("time").findtext("beats"))
					beat_type = int(event.find("time").findtext("beat-type"))
				if event.find("key") != None:
					key = int(event.find("key").findtext("fifths"))
				
				score_info = XmlScore(divisions, beats, beat_type, key)

			# getting chord attributes
			if event.tag == "harmony":
				if event.find("root") != None:
					chord_root_step = event.find("root").findtext("root-step")
					chord_root_alter = event.find("root").findtext("root-alter")
					if chord_root_alter == None:	# if alter is not indicated, there's no alteration and we consider the value 0
						chord_root_alter = 0
					chord_root_alter = int(chord_root_alter)
					chord_kind = event.findtext("kind")

					new_chord = XmlChord(chord_root_step, chord_root_alter, chord_kind)
					new_chord.addTimestamp(global_clock)
					chord_list.append(new_chord)	# adding the chord to the list of chords

			# getting note attributes
			if event.tag == "note":
				if event.find("pitch") != None:		# if there's a pitch, it's a note
					note_step = event.find("pitch").findtext("step")
					note_alter = event.find("pitch").findtext("alter")
					if note_alter == None:		# if alter in not indicated, there's no alteration and we consider the value 0
						note_alter = 0
					note_alter = int(note_alter)
					note_octave = int(event.find("pitch").findtext("octave"))
					note_duration = int(event.findtext("duration"))

					# Unification with the previous note if they are tied
					if event.find("notations") != None:
						global_tied = global_tied + len(event.find("notations").findall("tied"))
					if global_tied >= 2:	#if this note is tied to the previous one, we don't create a new note but add its duration to the previous one
						global_tied = global_tied - 2
						note_list[-1].changeDuration(note_list[-1].duration + note_duration)
					else:	#if the note isn't tied we add it to the list
						new_note = XmlNote(note_step, note_alter, note_octave, note_duration)
						new_note.addTimestamp(global_clock)
						note_list.append(new_note)
				else:	# if there's no pitch, it's a rest
					note_step = "Rest"
					note_alter = None
					note_octave = None
					note_duration = int(event.findtext("duration"))

					# Unification with the previous rest if previous note was also a rest
					if note_list !=[] and note_list[-1].step == "Rest":
						note_list[-1].changeDuration(note_list[-1].duration + note_duration)
					else :
						new_note = XmlNote(note_step, note_alter, note_octave, note_duration)
						new_note.addTimestamp(global_clock)
						note_list.append(new_note)

				global_clock = global_clock + note_duration

	return (score_info, chord_list, note_list)

######## ######## ########
