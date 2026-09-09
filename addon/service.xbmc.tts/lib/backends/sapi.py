# -*- coding: utf-8 -*-
"""Windows SAPI backend for Kodi's embedded Python 3 runtime.

The original add-on bundled a Python-2-only comtypes copy.  This backend uses
Windows PowerShell's built-in System.Speech bridge instead, so it needs no
third-party Python COM package.
"""

import base64
import os
import subprocess
import sys

from base import SimpleTTSBackendBase
from lib import util


class SAPITTSBackend(SimpleTTSBackendBase):
    provider = 'SAPI'
    displayName = 'SAPI (Windows Internal)'
    settings = {
        # Direct Windows output is more reliable than the add-on's legacy
        # PlaySFX route on Kodi 21.
        'speak_via_xbmc': False,
        'voice': '',
        'speed': 0,
        'pitch': 0,
        'volume': 100,
    }
    canStreamWav = True
    speedConstraints = (-10, 0, 10, True)
    pitchConstraints = (-10, 0, 10, True)
    volumeConstraints = (0, 100, 100, True)
    volumeExternalEndpoints = (0, 100)
    volumeStep = 5
    volumeSuffix = '%'

    def init(self):
        self.update()

    @staticmethod
    def available():
        return sys.platform.lower().startswith('win')

    def update(self):
        self.setMode(self.getMode())

    def getMode(self):
        return self.WAVOUT if self.setting('speak_via_xbmc') else self.ENGINESPEAK

    def _encoded_command(self, text, out_file=None):
        # Base64 keeps arbitrary screen text out of the PowerShell command line.
        text64 = base64.b64encode(text.encode('utf-8')).decode('ascii')
        lines = [
            '$ErrorActionPreference = "Stop"',
            'Add-Type -AssemblyName System.Speech',
            '$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer',
            '$voice.Rate = {0}'.format(int(self.setting('speed') or 0)),
            '$voice.Volume = {0}'.format(int(self.setting('volume') or 100)),
        ]
        voice_name = self.setting('voice')
        if voice_name:
            voice64 = base64.b64encode(voice_name.encode('utf-8')).decode('ascii')
            lines.append('$voice.SelectVoice([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("{0}")))'.format(voice64))
        if out_file:
            file64 = base64.b64encode(out_file.encode('utf-8')).decode('ascii')
            lines.append('$voice.SetOutputToWaveFile([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("{0}")))'.format(file64))
        lines.extend([
            '$text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("{0}"))'.format(text64),
            '$voice.Speak($text)',
            '$voice.Dispose()',
        ])
        return base64.b64encode('; '.join(lines).encode('utf-16le')).decode('ascii')

    def _run(self, text, out_file=None):
        try:
            if out_file and os.path.exists(out_file):
                os.remove(out_file)
            command = self._encoded_command(text, out_file)
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            result = subprocess.run(
                ['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=flags,
            )
            if result.returncode != 0:
                util.LOG('SAPI fallback failed: {0}'.format(result.stderr.decode('utf-8', 'replace')))
                return False
            return not out_file or os.path.exists(out_file)
        except Exception as exc:
            util.LOG('SAPI fallback failed: {0}'.format(exc))
            return False

    def runCommand(self, text, outFile):
        return self._run(text, outFile)

    def runCommandAndSpeak(self, text):
        self._run(text)

    @classmethod
    def settingList(cls, setting, *args):
        return []
