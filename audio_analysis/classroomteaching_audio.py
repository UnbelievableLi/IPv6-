# -*- coding: utf-8 -*-
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # tensorflow base_logging INFO 0 WARNING 1 ERROR 2 FATAL 3

import subprocess
import sys
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path, PurePath
from tqdm.autonotebook import tqdm
from simple_diarizer.diarizer import Diarizer
from simple_diarizer.utils import combined_waveplot, check_wav_16khz_mono

from asrt.speech_model import ModelSpeech
from asrt.speech_model_zoo import SpeechModel251
from asrt.speech_features import Spectrogram


class AudioAnalyzeClassTeaching:
    audioFilePath = ''
    wavOrigFilePath = ''
    wavNsFilePath = ''
    wavOrigSignal = []
    wavNsSignal = []
    wavSampleRate = 0
    wavDiarizeSeg = [] # {'beginSample': , 'endSample': , 'labelSpeaker': , 'numberPinyin': }
    diarizeNumberLabel = -1
    diarizeTeacherLabel = -1
    lessonStudentNumber = 0
    paramStudyTeach = {}

    def __init__(self, audioFile, studentNumber=0):
        self.wavSampleRate = 16000
        self.audioFilePath = audioFile
        self.lessonStudentNumber = int(studentNumber)

    def NoiseSupressWav(self, force=False, voiceFilter=False, verbose=False):
        audioFileStem = PurePath(self.audioFilePath).stem
        audioFileOrigPcm = audioFileStem + '_orig.pcm'
        audioFileOrigWav = audioFileStem + '_orig.wav'
        audioFileNsPcm = audioFileStem + '_ns.pcm'
        audioFileNsWav = audioFileStem + '_ns.wav'
        levelLogFfmpeg = '-v info' if verbose else '-v warning'
        if force or not(Path(audioFileOrigWav).is_file() and Path(audioFileNsWav).is_file() and check_wav_16khz_mono(audioFileNsWav)):
            audioWavPcm = 'ffmpeg {} -y -i {} -f s16le -ar {} -ac 1 {}'.format(levelLogFfmpeg, self.audioFilePath, self.wavSampleRate, audioFileOrigPcm)
            subprocess.run(audioWavPcm, shell=True)
            assert Path(audioFileOrigPcm).is_file(), 'Failed to convert to pcm.'
            audioPcmWav = 'ffmpeg {} -y -f s16le -ar {} -ac 1 -i {} {}'.format(levelLogFfmpeg, self.wavSampleRate, audioFileOrigPcm, audioFileOrigWav)
            subprocess.run(audioPcmWav, shell=True)
            assert Path(audioFileOrigWav).is_file(), 'Failed to convert pcm to wav.'
            audioNsWebRTC = 'webrtc_apm_win ns {} {}'.format(audioFileOrigPcm, audioFileNsPcm)
            subprocess.run(audioNsWebRTC, shell=True)
            assert Path(audioFileNsPcm).is_file(), 'Failed to generate noise suppressed pcm.'
            audioNsPcmWav = 'ffmpeg {} -y -f s16le -ar {} -ac 1 -i {} {}'.format(levelLogFfmpeg, self.wavSampleRate, audioFileNsPcm, audioFileNsWav)
            subprocess.run(audioNsPcmWav, shell=True)
            assert Path(audioFileNsWav).is_file(), 'Failed to convert pcm to wav.'
            Path(audioFileOrigPcm).unlink()
            Path(audioFileNsPcm).unlink()
            if voiceFilter:
                wavSignal, sampleRate = sf.read(audioFileNsWav, dtype='float32')
                wavRfft = np.fft.rfft(wavSignal)
                wavRfftFreq = np.fft.rfftfreq(wavSignal.size, d=1./sampleRate)
                # wavNoiseIndex = np.flatnonzero(np.logical_or(300 > wavRfftFreq, 3400 < wavRfftFreq))
                wavNoiseIndex = np.flatnonzero(np.logical_or(50 > wavRfftFreq, 4000 < wavRfftFreq))
                wavRfft[wavNoiseIndex] = 0
                wavIrfft = np.fft.irfft(wavRfft)
                sf.write(audioFileNsWav, wavIrfft, sampleRate)
        self.wavOrigFilePath = audioFileOrigWav
        self.wavNsFilePath = audioFileNsWav

    def WavRead(self):
        self.wavOrigSignal, wavOrigSampleRate = sf.read(self.wavOrigFilePath, dtype='int16')
        assert wavOrigSampleRate == self.wavSampleRate, 'WAV file sample rate error.'
        self.wavNsSignal, wavNsSampleRate = sf.read(self.wavNsFilePath, dtype='int16')
        assert wavNsSampleRate == self.wavSampleRate, 'WAV file sample rate error.'

    def SimpleDiarize(self, clusterMethod='sc', windowPeriod=0.75, numSpeaker=2, numSpeakerUlt=50, wavePlot=False):
        diar = Diarizer(embed_model='xvec', cluster_method=clusterMethod, window=2*windowPeriod, period=windowPeriod)
        # diar = Diarizer(embed_model='xvec', cluster_method='sc', window=1.5, period=0.75)
        diarizeSeg = diar.diarize(self.wavNsFilePath, num_speakers=numSpeaker, num_speakers_ult=numSpeakerUlt) # {'start': , 'end': , 'label': , 'start_sample': , 'end_sample': }
        for i in diarizeSeg:
            self.wavDiarizeSeg.append({'beginSample': i['start_sample'], 'endSample': i['end_sample'], 'labelSpeaker': i['label']})
        self.wavDiarizeSeg.sort(key=(lambda elem: elem['beginSample']))
        if wavePlot:
            combined_waveplot(self.wavNsSignal, self.wavSampleRate, diarizeSeg)
            plt.show()

    def PredictSpeechPinyin(self):
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        audioLength = 1600
        audioFeatureLength = 200
        audioChannel = 1
        outputSize = 1428
        sm251 = SpeechModel251(input_shape=(audioLength, audioFeatureLength, audioChannel), output_size=outputSize)
        feat = Spectrogram()
        speech251Spectro = ModelSpeech(sm251, feat, max_label_length=64)
        speech251Spectro.load_model('asrt11/' + 'save_models/' + sm251.get_model_name() + '.model.h5')
        for i in tqdm(iterable=self.wavDiarizeSeg, desc='Speech recognition'):
        # for i in self.wavDiarizeSeg:
            speechPinyin = []
            sampleSignal = self.wavNsSignal[i['beginSample'] : i['endSample']]
            sampleSegmentNumber = (int(sampleSignal.size / 16 - 25) // 10 + 1) // 1600 + 1
            sampleSegmentLength = sampleSignal.size // ((int(sampleSignal.size / 16 - 25) // 10 + 1) // 1600 + 1) + 1
            for j in range(sampleSegmentNumber - 1):
                speechPinyin.extend(speech251Spectro.recognize_speech(sampleSignal[j * sampleSegmentLength : (j + 1) * sampleSegmentLength].reshape(1, sampleSegmentLength), self.wavSampleRate))
            if (sampleSegmentNumber - 1) * sampleSegmentLength < sampleSignal.size:
                speechPinyin.extend(speech251Spectro.recognize_speech(sampleSignal[(sampleSegmentNumber - 1) * sampleSegmentLength : sampleSignal.size].reshape(1, sampleSignal.size - (sampleSegmentNumber - 1) * sampleSegmentLength), self.wavSampleRate))
            i['numberPinyin'] = len(speechPinyin)

    def TeacherSpeaker(self, verbose=False):
        countSpeaker = {}
        for i in self.wavDiarizeSeg:
            if i['labelSpeaker'] in countSpeaker:
                countSpeaker[i['labelSpeaker']] = countSpeaker[i['labelSpeaker']] + 1
            else:
                countSpeaker[i['labelSpeaker']] = 1
        self.diarizeNumberLabel = len(countSpeaker)
        majorSpeaker = 0
        for i in countSpeaker:
            if majorSpeaker < countSpeaker[i]:
                majorSpeaker = countSpeaker[i]
                self.diarizeTeacherLabel = i
        if verbose:
            print('Label number: {}, teacher label: {}.'.format(self.diarizeNumberLabel, self.diarizeTeacherLabel))

    def WavTimeVolume(self, verbose=False):
        wavLengthTime = self.wavOrigSignal.size / self.wavSampleRate
        wavSampleAmplitude = np.asarray(self.wavOrigSignal, dtype=np.int16)
        wavAverageVolume = 20 * np.log10(np.mean(np.abs(wavSampleAmplitude)))
        if verbose:
            print('Audio time length: {}s, average volume: {}dB.'.format(wavLengthTime, wavAverageVolume))
        self.paramStudyTeach['wavLengthTime'] = wavLengthTime
        self.paramStudyTeach['wavAverageVolume'] = wavAverageVolume

    def TeacherStudentInteract(self, verbose=False):
        speakerLabel = np.asarray([], dtype=np.int16)
        activeBeginSample = np.asarray([], dtype=np.int32)
        activeEndSample = np.asarray([], dtype=np.int32)
        activeEndSample = np.append(activeEndSample, 0) # Before voice activity detected
        for i in self.wavDiarizeSeg:
            speakerLabel = np.append(speakerLabel, i['labelSpeaker'])
            activeBeginSample = np.append(activeBeginSample, i['beginSample'])
            activeEndSample = np.append(activeEndSample, i['endSample'])
        activeBeginSample = np.append(activeBeginSample, self.wavNsSignal.size) # After voice activity detected
        diarizeSegmentNumber = speakerLabel.size
        teacherSegmentNumber = np.count_nonzero(speakerLabel == self.diarizeTeacherLabel)
        speakerInteractNumber = np.count_nonzero(0 != (speakerLabel[1 : ] - speakerLabel[ : -1]))
        intervalSample = activeBeginSample - activeEndSample
        intervalSumTime = np.sum(intervalSample) / self.wavSampleRate
        intervalAverageTime = np.mean(intervalSample) / self.wavSampleRate
        interactSpeakerPair = np.asarray([speakerLabel[ : -1], speakerLabel[1 : ]])
        interactFromTeacherToStudent = np.compress(np.logical_and(interactSpeakerPair[0] == self.diarizeTeacherLabel, interactSpeakerPair[1] != self.diarizeTeacherLabel), interactSpeakerPair.T, axis=0).T[1]
        interactCountTeacherToStudent = np.asarray([], dtype=np.int32)
        for ts in range(self.diarizeNumberLabel):
            interactCountTeacherToStudent = np.append(interactCountTeacherToStudent, np.count_nonzero(ts == interactFromTeacherToStudent))
        interactAverageTeacherToStudent = np.mean(interactCountTeacherToStudent)
        interactDeviationTeacherToStudent = np.std(interactCountTeacherToStudent)
        if verbose:
            print('Class diarized segments number: {}, teacher diarized segments number: {}, teacher and students interaction: {}times, total interval time: {}s, average interval time: {}s.'.format(diarizeSegmentNumber, teacherSegmentNumber, speakerInteractNumber, intervalSumTime, intervalAverageTime))
            print('Interact counts from teacher to student average: {}, deviation: {}.'.format(interactAverageTeacherToStudent, interactDeviationTeacherToStudent))
        self.paramStudyTeach['diarizeSegmentNumber'] = diarizeSegmentNumber
        self.paramStudyTeach['teacherSegmentNumber'] = teacherSegmentNumber
        self.paramStudyTeach['speakerInteractNumber'] = speakerInteractNumber
        self.paramStudyTeach['intervalSumTime'] = intervalSumTime
        self.paramStudyTeach['intervalAverageTime'] = intervalAverageTime
        self.paramStudyTeach['interactCountTeacherToStudent'] = interactCountTeacherToStudent
        self.paramStudyTeach['interactAverageTeacherToStudent'] = interactAverageTeacherToStudent
        self.paramStudyTeach['interactDeviationTeacherToStudent'] = interactDeviationTeacherToStudent

    def StudentTeacherTimeVolume(self, verbose=False):
        studentSample = np.asarray([], dtype=np.int32)
        studentAmplitude = np.asarray([], dtype=np.int16)
        teacherSample = np.asarray([], dtype=np.int32)
        teacherAmplitude = np.asarray([], dtype=np.int16)
        for i in self.wavDiarizeSeg:
            if self.diarizeTeacherLabel != i['labelSpeaker']:
                studentSample = np.append(studentSample, (i['endSample'] - i['beginSample']))
                studentAmplitude = np.append(studentAmplitude, self.wavOrigSignal[i['beginSample'] : i['endSample']])
            else:
                teacherSample = np.append(teacherSample, (i['endSample'] - i['beginSample']))
                teacherAmplitude = np.append(teacherAmplitude, self.wavOrigSignal[i['beginSample'] : i['endSample']])
        studentSpeakingTime = np.sum(studentSample) / self.wavSampleRate
        studentAverageTime = np.mean(studentSample) / self.wavSampleRate
        studentAverageVolume = 20 * np.log10(np.mean(np.abs(studentAmplitude)))
        teacherSpeakingTime = np.sum(teacherSample) / self.wavSampleRate
        teacherAverageTime = np.mean(teacherSample) / self.wavSampleRate
        teacherAverageVolume = 20 * np.log10(np.mean(np.abs(teacherAmplitude)))
        if verbose:
            print('Student total speaking time: {}s, average speaking time: {}s, average volume: {}dB.'.format(studentSpeakingTime, studentAverageTime, studentAverageVolume))
            print('Teacher total speaking time: {}s, average speaking time: {}s, average volume: {}dB.'.format(teacherSpeakingTime, teacherAverageTime, teacherAverageVolume))
        self.paramStudyTeach['studentSpeakingTime'] = studentSpeakingTime
        self.paramStudyTeach['studentAverageTime'] = studentAverageTime
        self.paramStudyTeach['studentAverageVolume'] = studentAverageVolume
        self.paramStudyTeach['teacherSpeakingTime'] = teacherSpeakingTime
        self.paramStudyTeach['teacherAverageTime'] = teacherAverageTime
        self.paramStudyTeach['teacherAverageVolume'] = teacherAverageVolume

    def TeacherVolumeFeature(self, verbose=False):
        teacherVolume = np.asarray([], dtype=np.float32)
        for i in self.wavDiarizeSeg:
            if self.diarizeTeacherLabel == i['labelSpeaker']:
                teacherVolume = np.append(teacherVolume, 20 * np.log10(np.mean(np.abs(np.asarray(self.wavOrigSignal[i['beginSample'] : i['endSample']], np.int16)))))
        teacherDeviationVolume = np.std(teacherVolume)
        teacherDifferentialVolume = np.sqrt(np.mean((teacherVolume[1 : ] - teacherVolume[ : -1]) ** 2))
        if verbose:
            print('Teacher volume standard deviation: {}dB, differential root mean square: {}dB.'.format(teacherDeviationVolume, teacherDifferentialVolume))
        self.paramStudyTeach['teacherDeviationVolume'] = teacherDeviationVolume
        self.paramStudyTeach['teacherDifferentialVolume'] = teacherDifferentialVolume

    def StudentTeacherSpeechPinyin(self, verbose=False, speechRateThreshold=(2.5, 3.5)):
        assert(0 <= speechRateThreshold[0] and 0 < speechRateThreshold[1])
        studentSpeechPinyin = np.asarray([], dtype=np.int16)
        studentSpeechSample = np.asarray([], dtype=np.int32)
        teacherSpeechPinyin = np.asarray([], dtype=np.int16)
        teacherSpeechSample = np.asarray([], dtype=np.int32)
        for i in self.wavDiarizeSeg:
            if self.diarizeTeacherLabel != i['labelSpeaker']:
                studentSpeechPinyin = np.append(studentSpeechPinyin, i['numberPinyin'])
                studentSpeechSample = np.append(studentSpeechSample, i['endSample'] - i['beginSample'])
            else:
                teacherSpeechPinyin = np.append(teacherSpeechPinyin, i['numberPinyin'])
                teacherSpeechSample = np.append(teacherSpeechSample, i['endSample'] - i['beginSample'])
        studentSpeechRate = studentSpeechPinyin / studentSpeechSample * self.wavSampleRate
        studentTotalPinyin = np.sum(studentSpeechPinyin)
        studentAverageRate = studentTotalPinyin / np.sum(studentSpeechSample) * self.wavSampleRate
        studentDeviationRate = np.std(studentSpeechRate)
        studentSpeechEmotion = np.where(np.logical_and(studentSpeechRate >= speechRateThreshold[0], studentSpeechRate < speechRateThreshold[1]), 3., studentSpeechRate)
        studentSpeechEmotion = np.where(studentSpeechRate < speechRateThreshold[0], 2., studentSpeechEmotion)
        studentSpeechEmotion = np.where(studentSpeechRate >= speechRateThreshold[1], 4., studentSpeechEmotion)
        studentSpeechEmotion = np.asarray(studentSpeechEmotion, dtype=np.int)
        studentExcitedTime = np.sum(np.extract(4 == studentSpeechEmotion, studentSpeechSample)) / self.wavSampleRate
        teacherSpeechRate = teacherSpeechPinyin / teacherSpeechSample * self.wavSampleRate
        teacherTotalPinyin = np.sum(teacherSpeechPinyin)
        teacherAverageRate = teacherTotalPinyin / np.sum(teacherSpeechSample) * self.wavSampleRate
        teacherDeviationRate = np.std(teacherSpeechRate)
        teacherSpeechEmotion = np.where(np.logical_and(teacherSpeechRate >= speechRateThreshold[0], teacherSpeechRate < speechRateThreshold[1]), 3., teacherSpeechRate)
        teacherSpeechEmotion = np.where(teacherSpeechRate < speechRateThreshold[0], 2., teacherSpeechEmotion)
        teacherSpeechEmotion = np.where(teacherSpeechRate >= speechRateThreshold[1], 4., teacherSpeechEmotion)
        teacherSpeechEmotion = np.asarray(teacherSpeechEmotion, dtype=np.int)
        teacherExcitedTime = np.sum(np.extract(4 == teacherSpeechEmotion, teacherSpeechSample)) / self.wavSampleRate
        teacherEmotionAlter = np.count_nonzero(teacherSpeechEmotion[1 : ] - teacherSpeechEmotion[ : -1])
        if verbose:
            print('Student total words (Chinese characters) spoken: {}character, speech rate: {}character/s, speech rate standard deviation: {}character/s, excited emotion time: {}s.'.format(studentTotalPinyin, studentAverageRate, studentDeviationRate, studentExcitedTime))
            print('Teacher total words (Chinese characters) spoken: {}character, speech rate: {}character/s, speech rate standard deviation: {}character/s, excited emotion time: {}s, emotion alter number: {}.'.format(teacherTotalPinyin, teacherAverageRate, teacherDeviationRate, teacherExcitedTime, teacherEmotionAlter))
        self.paramStudyTeach['studentTotalPinyin'] = studentTotalPinyin
        self.paramStudyTeach['studentAverageRate'] = studentAverageRate
        self.paramStudyTeach['studentDeviationRate'] = studentDeviationRate
        self.paramStudyTeach['studentExcitedTime'] = studentExcitedTime
        self.paramStudyTeach['teacherTotalPinyin'] = teacherTotalPinyin
        self.paramStudyTeach['teacherAverageRate'] = teacherAverageRate
        self.paramStudyTeach['teacherDeviationRate'] = teacherDeviationRate
        self.paramStudyTeach['teacherExcitedTime'] = teacherExcitedTime
        self.paramStudyTeach['teacherEmotionAlter'] = teacherEmotionAlter

    def AnalyzeStudyTeach(self, volumeRatioThreshold=1.5, emotionExcitedThreshold=(66.7, 75.), emotionAlterThreshold=.5, deviationVolumeThreshold=5.):
        teacherSpeechPercent = self.paramStudyTeach['teacherSpeakingTime'] / self.paramStudyTeach['wavLengthTime'] * 100
        studentSpeechPercent = self.paramStudyTeach['studentSpeakingTime'] / self.paramStudyTeach['wavLengthTime'] * 100
        intervalSpeechPercent = self.paramStudyTeach['intervalSumTime'] / self.paramStudyTeach['wavLengthTime'] * 100
        print('教师语音时间占比{}%，学生语音时间占比{}%，间隔（安静）时间占比{}%。'.format(round(teacherSpeechPercent, 3), round(studentSpeechPercent, 3), round(intervalSpeechPercent, 3)))
        print('教师语音平均音量{}dB，学生语音平均音量{}dB。'.format(round(self.paramStudyTeach['teacherAverageVolume'], 3), round(self.paramStudyTeach['studentAverageVolume'], 3)))
        print('教师语音字数{}字，平均语速{}字/秒；学生语音字数{}字，平均语速{}字/秒。'.format(self.paramStudyTeach['teacherTotalPinyin'], round(self.paramStudyTeach['teacherAverageRate'], 3), self.paramStudyTeach['studentTotalPinyin'], round(self.paramStudyTeach['studentAverageRate'], 3)))
        stAnalysisRt = self.paramStudyTeach['teacherSpeakingTime'] / self.paramStudyTeach['wavLengthTime']
        stAnalysisCh = self.paramStudyTeach['speakerInteractNumber'] / self.paramStudyTeach['diarizeSegmentNumber']
        stTeachingModel = lambda stRt, stCh: '练习型' if 0.3 >= stRt else ('讲授型' if 0.7 <= stRt else ('对话型' if 0.4 <= stCh else '混合型'))
        print('S-T教学分析法：教师行为占有率{}，行为转换率{}，教学模式划分为{}。'.format(round(stAnalysisRt, 3), round(stAnalysisCh, 3), stTeachingModel(stAnalysisRt, stAnalysisCh)))
        lessonInteractFreq = self.paramStudyTeach['speakerInteractNumber'] / (self.paramStudyTeach['teacherSpeakingTime'] + self.paramStudyTeach['studentSpeakingTime'])
        lessonInteractDens = self.paramStudyTeach['speakerInteractNumber'] / self.diarizeNumberLabel
        lessonTchStuInteractDens = self.paramStudyTeach['interactAverageTeacherToStudent']
        lessonTchStuInteractConc = 1. / self.paramStudyTeach['interactDeviationTeacherToStudent']
        print('课堂交互频度{}，课堂交互密度{}，师生交互密度{}，师生交互集中度{}。'.format(round(lessonInteractFreq, 3), round(lessonInteractDens, 3), round(lessonTchStuInteractDens, 3), round(lessonTchStuInteractConc, 3)))
        emoStudentExcitedTimePercent = self.paramStudyTeach['studentExcitedTime'] / self.paramStudyTeach['studentSpeakingTime'] * 100
        emoTeacherExcitedTimePercent = self.paramStudyTeach['teacherExcitedTime'] / self.paramStudyTeach['teacherSpeakingTime'] * 100
        emoTeacherEmotionAlterRate = self.paramStudyTeach['teacherEmotionAlter'] / self.paramStudyTeach['teacherSegmentNumber']
        emoTeacherEmotionOverall = '兴奋' if ((emotionExcitedThreshold[1] < emoTeacherExcitedTimePercent) or ((emotionExcitedThreshold[0] < emoTeacherExcitedTimePercent) and (emotionAlterThreshold < emoTeacherEmotionAlterRate)) or (deviationVolumeThreshold < self.paramStudyTeach['teacherDeviationVolume'])) else '平静'
        print('学生语音兴奋时间占比{}%，教师语音兴奋时间占比{}%，教师情绪转换率{}，教师音量变化度{}dB，教师总体情绪较{}。'.format(round(emoStudentExcitedTimePercent, 3), round(emoTeacherExcitedTimePercent, 3), round(emoTeacherEmotionAlterRate, 3), round(self.paramStudyTeach['teacherDeviationVolume'], 3), emoTeacherEmotionOverall))
        if self.lessonStudentNumber:
            lessonSpeakPercent = (self.diarizeNumberLabel - 1) / self.lessonStudentNumber * 100
            print('课堂发言比例{}%。'.format(round(lessonSpeakPercent, 3)))

    def CleanFileTmp(self):
        Path(self.wavOrigFilePath).unlink()
        Path(self.wavNsFilePath).unlink()

    def AnalyzeClassTeaching(self):
        self.NoiseSupressWav(force=False, voiceFilter=False, verbose=False)
        self.WavRead()
        lessonTeacherStudentNumber = self.lessonStudentNumber + 1 if self.lessonStudentNumber else 50
        self.SimpleDiarize(clusterMethod='ahc', windowPeriod=0.75, numSpeaker=2, numSpeakerUlt=lessonTeacherStudentNumber, wavePlot=False)
        # print(self.wavDiarizeSeg)
        self.PredictSpeechPinyin()
        paramVerbosePrint = False
        self.TeacherSpeaker(verbose=paramVerbosePrint)
        self.WavTimeVolume(verbose=paramVerbosePrint)
        self.TeacherStudentInteract(verbose=paramVerbosePrint)
        self.StudentTeacherTimeVolume(verbose=paramVerbosePrint)
        self.TeacherVolumeFeature(verbose=paramVerbosePrint)
        self.StudentTeacherSpeechPinyin(verbose=paramVerbosePrint, speechRateThreshold=(2.5, 3.5))
        if paramVerbosePrint:
            print(self.paramStudyTeach)
        self.AnalyzeStudyTeach(volumeRatioThreshold=1.5, emotionExcitedThreshold=(66.7, 75.), emotionAlterThreshold=.5, deviationVolumeThreshold=5.)
        # self.CleanFileTmp()


if __name__ == "__main__":
    if 2 == len(sys.argv):
        aact = AudioAnalyzeClassTeaching(sys.argv[1])
        aact.AnalyzeClassTeaching()
    elif 3 == len(sys.argv):
        aact = AudioAnalyzeClassTeaching(sys.argv[1], sys.argv[2])
        aact.AnalyzeClassTeaching()
    else:
        print('{} <audio file> [<student number>]'.format(sys.argv[0]))


