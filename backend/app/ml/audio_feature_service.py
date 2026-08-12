from pathlib import Path
from typing import Dict, List, Union

import librosa
import numpy as np


class AudioFeatureService:
    """
    Audio preprocessing and feature extraction service.

    The final output must contain exactly the 22 features
    expected by the Parkinson ML model.
    """

    FEATURE_NAMES = [
        "MDVP:Fo(Hz): Average fundamental frequency",
        "MDVP:Fhi(Hz): Maximum fundamental frequency",
        "MDVP:Flo(Hz): Minimum fundamental frequency",
        "MDVP:Jitter(%): Percentage variation",
        "MDVP:Jitter(Abs): Absolute variation",
        "MDVP:RAP: Relative Average Perturbation",
        "MDVP:PPQ: Pitch Period Perturbation",
        "Jitter:DDP: Average pitch variation",
        "MDVP:Shimmer: Amplitude variation",
        "MDVP:Shimmer(dB): Shimmer in decibels",
        "Shimmer:APQ3: Three-point amplitude quotient",
        "Shimmer:APQ5: Five-point amplitude quotient",
        "Shimmer:APQ5: Five-point amplitude quotient",
        "Shimmer:APQ5: Five-point amplitude quotient",
        "MDVP:APQ: Amplitude Perturbation Quotient",
        "Shimmer:DDA: Average amplitude variation",
        "NHR: Noise-to-Harmonics Ratio",
        "HNR: Harmonics-to-Noise Ratio",
        "RPDE: Recurrence Period Density Entropy",
        "DFA: Detrended Fluctuation Analysis",
        "Spread1: Nonlinear frequency variation",
        "Spread2: Nonlinear voice characteristic",
        "D2: Correlation Dimension",
        "PPE: Pitch Period Entropy",
    ]

    SAMPLE_RATE = 22050

    MIN_DURATION_SECONDS = 1.0

    MAX_DURATION_SECONDS = 60.0

    def load_audio(
        self,
        audio_path: Union[str, Path],
    ):
        """
        Load an audio file as a mono waveform.
        """

        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {path}"
            )

        try:
            audio, sample_rate = librosa.load(
                path,
                sr=self.SAMPLE_RATE,
                mono=True,
            )
        except Exception as exc:
            raise ValueError(
                f"Unable to read audio file: {exc}"
            ) from exc

        if audio is None or len(audio) == 0:
            raise ValueError(
                "Audio file contains no usable samples."
            )

        duration = len(audio) / sample_rate

        if duration < self.MIN_DURATION_SECONDS:
            raise ValueError(
                "Audio recording is too short. "
                f"Minimum duration is "
                f"{self.MIN_DURATION_SECONDS} seconds."
            )

        if duration > self.MAX_DURATION_SECONDS:
            raise ValueError(
                "Audio recording is too long. "
                f"Maximum duration is "
                f"{self.MAX_DURATION_SECONDS} seconds."
            )

        return audio, sample_rate

    def validate_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> None:
        """
        Validate the loaded waveform.
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if len(audio) == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid sample rate."
            )

        if not np.isfinite(audio).all():
            raise ValueError(
                "Audio contains invalid numeric values."
            )

        peak = float(
            np.max(
                np.abs(audio)
            )
        )

        if peak == 0:
            raise ValueError(
                "Audio is silent."
            )

    def normalize_audio(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:
        """
        Normalize waveform amplitude.
        """

        peak = float(
            np.max(
                np.abs(audio)
            )
        )

        if peak <= 0:
            raise ValueError(
                "Cannot normalize silent audio."
            )

        return audio / peak

    def extract_basic_voice_features(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> Dict[str, float]:
        """
        Extract the basic acoustic measurements that
        can be calculated reliably from the waveform.

        This method intentionally does NOT fabricate
        RPDE, DFA, spread1, spread2, D2, or PPE.
        """

        audio = self.normalize_audio(
            audio
        )

        # Fundamental frequency estimation.
        f0, voiced_flag, voiced_prob = (
            librosa.pyin(
                audio,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                sr=sample_rate,
            )
        )

        voiced_f0 = f0[
            np.isfinite(f0)
        ]

        if len(voiced_f0) == 0:
            raise ValueError(
                "Unable to detect a usable "
                "fundamental frequency from "
                "the recording."
            )

        fo = float(
            np.mean(voiced_f0)
        )

        fhi = float(
            np.max(voiced_f0)
        )

        flo = float(
            np.min(voiced_f0)
        )

        # RMS energy.
        rms = librosa.feature.rms(
            y=audio
        )[0]

        rms = rms[
            np.isfinite(rms)
        ]

        if len(rms) == 0:
            raise ValueError(
                "Unable to calculate RMS energy."
            )

        # Zero-crossing rate.
        zcr = librosa.feature.zero_crossing_rate(
            audio
        )[0]

        zcr = zcr[
            np.isfinite(zcr)
        ]

        # Spectral features.
        spectral_centroid = (
            librosa.feature.spectral_centroid(
                y=audio,
                sr=sample_rate,
            )[0]
        )

        spectral_centroid = (
            spectral_centroid[
                np.isfinite(
                    spectral_centroid
                )
            ]
        )

        if len(
            spectral_centroid
        ) == 0:
            raise ValueError(
                "Unable to calculate "
                "spectral features."
            )

        return {
            "MDVP:Fo(Hz)": fo,

            "MDVP:Fhi(Hz)": fhi,

            "MDVP:Flo(Hz)": flo,

            # These are placeholders only in
            # the returned diagnostic structure.
            #
            # They MUST NOT be passed to the
            # trained model until properly
            # implemented.
            "rms_mean": float(
                np.mean(rms)
            ),

            "rms_std": float(
                np.std(rms)
            ),

            "zcr_mean": float(
                np.mean(zcr)
            ),

            "spectral_centroid_mean": float(
                np.mean(
                    spectral_centroid
                )
            ),
        }

    def extract(
        self,
        audio_path: Union[str, Path],
    ) -> Dict[str, float]:
        """
        Load and analyze an audio recording.

        At this stage this method intentionally raises
        an error because the complete 22-feature mapping
        has not yet been implemented.
        """

        audio, sample_rate = (
            self.load_audio(
                audio_path
            )
        )

        self.validate_audio(
            audio,
            sample_rate,
        )

        basic_features = (
            self.extract_basic_voice_features(
                audio,
                sample_rate,
            )
        )

        raise NotImplementedError(
            "Complete 22-feature extraction is not "
            "implemented yet. Basic audio analysis "
            "completed successfully, but the model "
            "must not receive incomplete or fabricated "
            "features."
        )

    @classmethod
    def feature_names(cls) -> List[str]:
        """
        Return the exact model feature order.
        """

        return cls.FEATURE_NAMES.copy()

    @classmethod
    def feature_count(cls) -> int:
        """
        Return required feature count.
        """

        return len(
            cls.FEATURE_NAMES
        )
