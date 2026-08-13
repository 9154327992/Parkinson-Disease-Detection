# ==========================================================
# Audio Feature Service
# ==========================================================

from pathlib import Path
from typing import Dict, List, Tuple

import librosa
import numpy as np
import soundfile as sf


# ==========================================================
# Constants
# ==========================================================

TOTAL_FEATURES = 22

DEFAULT_SAMPLE_RATE = 22050

MIN_DURATION_SECONDS = 2.0

MAX_DURATION_SECONDS = 30.0

# ==========================================================
# Exact Model Feature Names
# ==========================================================

FEATURE_NAMES = [
    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",
    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",
    "NHR",
    "HNR",
    "RPDE",
    "DFA",
    "spread1",
    "spread2",
    "D2",
    "PPE",
]

# ==========================================================
# Feature Order Validation
# ==========================================================

if len(FEATURE_NAMES) != TOTAL_FEATURES:

    raise RuntimeError(
        "Feature configuration error: "
        f"expected {TOTAL_FEATURES} features, "
        f"found {len(FEATURE_NAMES)}."
    )


# ==========================================================
# Audio Feature Service
# ==========================================================

class AudioFeatureService:
    """
    Service responsible for converting an audio recording
    into the 22-feature structure expected by the
    Parkinson disease model.
    """

    TOTAL_FEATURES = TOTAL_FEATURES

    FEATURE_NAMES = FEATURE_NAMES.copy()

    DEFAULT_SAMPLE_RATE = (
        DEFAULT_SAMPLE_RATE
    )

    MIN_DURATION_SECONDS = (
        MIN_DURATION_SECONDS
    )

    MAX_DURATION_SECONDS = (
        MAX_DURATION_SECONDS
    )

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        min_duration: float = MIN_DURATION_SECONDS,
        max_duration: float = MAX_DURATION_SECONDS,
    ):
        """
        Initialize the audio feature service.
        """

        if sample_rate <= 0:

            raise ValueError(
                "Sample rate must be greater than zero."
            )

        if min_duration <= 0:

            raise ValueError(
                "Minimum duration must be greater than zero."
            )

        if max_duration <= min_duration:

            raise ValueError(
                "Maximum duration must be greater "
                "than minimum duration."
            )

        self.sample_rate = int(
            sample_rate
        )

        self.min_duration = float(
            min_duration
        )

        self.max_duration = float(
            max_duration
        )

    # ======================================================
    # Feature Count
    # ======================================================

    def get_feature_count(
        self,
    ) -> int:
        """
        Return the number of model features.
        """

        return TOTAL_FEATURES

    # ======================================================
    # Feature Names
    # ======================================================

    def get_feature_names(
        self,
    ) -> List[str]:
        """
        Return the exact model feature order.
        """

        return FEATURE_NAMES.copy()

# ==========================================================
# Audio Loading and Validation
# ==========================================================

    def load_audio(
        self,
        audio_path: str,
    ) -> Tuple[np.ndarray, int]:
        """
        Load an audio file as a mono waveform.
        """

        if not audio_path:

            raise ValueError(
                "Audio path is required."
            )

        path = Path(
            audio_path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {path}"
            )

        if not path.is_file():

            raise ValueError(
                f"Audio path is not a file: {path}"
            )

        try:

            audio, sample_rate = sf.read(
                str(path),
                dtype="float64",
                always_2d=False,
            )

        except Exception as exc:

            raise ValueError(
                f"Unable to read audio file: {path}"
            ) from exc

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.ndim == 2:

            audio = np.mean(
                audio,
                axis=1,
            )

        elif audio.ndim != 1:

            raise ValueError(
                "Audio must contain one or two dimensions."
            )

        sample_rate = int(
            sample_rate
        )

        self.validate_audio(
            audio,
            sample_rate,
        )

        return audio, sample_rate

# ==========================================================
# Validate Audio
# ==========================================================

    def validate_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> bool:
        """
        Validate an audio waveform before feature extraction.
        """

        if not isinstance(
            audio,
            np.ndarray,
        ):

            raise ValueError(
                "Audio waveform must be a NumPy array."
            )

        if audio.size == 0:

            raise ValueError(
                "Audio file contains no samples."
            )

        if sample_rate <= 0:

            raise ValueError(
                "Invalid audio sample rate."
            )

        if not np.isfinite(
            audio
        ).all():

            raise ValueError(
                "Audio contains invalid numeric values."
            )

        duration = (
            len(audio)
            / float(sample_rate)
        )

        if duration < self.min_duration:

            raise ValueError(
                "Audio recording is too short. "
                f"Minimum duration is "
                f"{self.min_duration:.1f} seconds."
            )

        if duration > self.max_duration:

            raise ValueError(
                "Audio recording is too long. "
                f"Maximum duration is "
                f"{self.max_duration:.1f} seconds."
            )

        peak = float(
            np.max(
                np.abs(audio)
            )
        )

        if peak <= 0:

            raise ValueError(
                "Audio recording is silent."
            )

        return True


# ==========================================================
# Validate Audio File
# ==========================================================

    def validate_audio_file(
        self,
        audio_path: str,
    ) -> bool:
        """
        Check that an audio file can be loaded and validated.
        """

        audio, sample_rate = (
            self.load_audio(
                audio_path
            )
        )

        return self.validate_audio(
            audio,
            sample_rate,
        )


# ==========================================================
# Audio Information
# ==========================================================

    def audio_information(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Return basic information about the audio.
        """

        duration = (
            len(audio)
            / float(sample_rate)
        )

        peak = float(
            np.max(
                np.abs(audio)
            )
        )

        rms = float(
            np.sqrt(
                np.mean(
                    audio ** 2
                )
            )
        )

        return {
            "sample_rate": int(
                sample_rate
            ),
            "samples": int(
                len(audio)
            ),
            "duration": float(
                duration
            ),
            "channels": 1,
            "peak": peak,
            "rms": rms,
        }


# ==========================================================
# Remove DC Offset
# ==========================================================

    def remove_dc_offset(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:
        """
        Remove the DC offset from the waveform.
        """

        return (
            audio
            - np.mean(audio)
        )


# ==========================================================
# Normalize Audio
# ==========================================================

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

            return audio

        return (
            audio / peak
        )

# ==========================================================
# Resample Audio
# ==========================================================

    def resample_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """
        Resample audio to the service sample rate.
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid source sample rate."
            )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.size == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        if sample_rate == self.sample_rate:
            return audio

        try:

            resampled = librosa.resample(
                audio,
                orig_sr=sample_rate,
                target_sr=self.sample_rate,
            )

        except Exception as exc:

            raise ValueError(
                "Unable to resample audio."
            ) from exc

        resampled = np.asarray(
            resampled,
            dtype=np.float64,
        )

        if resampled.size == 0:
            raise ValueError(
                "Resampling produced an empty waveform."
            )

        return resampled


# ==========================================================
# Preprocess Audio
# ==========================================================

    def preprocess_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> Tuple[np.ndarray, int]:
        """
        Prepare audio for feature extraction.

        Steps:
            1. Validate input
            2. Convert to mono if necessary
            3. Remove DC offset
            4. Resample
            5. Normalize amplitude
            6. Validate final waveform
        """

        self.validate_audio(
            audio,
            sample_rate,
        )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        # ------------------------------------------------------
        # Ensure mono
        # ------------------------------------------------------

        if audio.ndim == 2:

            audio = np.mean(
                audio,
                axis=1,
            )

        elif audio.ndim != 1:

            raise ValueError(
                "Audio must be mono or multi-channel."
            )

        # ------------------------------------------------------
        # Remove DC offset
        # ------------------------------------------------------

        audio = self.remove_dc_offset(
            audio
        )

        # ------------------------------------------------------
        # Resample
        # ------------------------------------------------------

        audio = self.resample_audio(
            audio,
            sample_rate,
        )

        # ------------------------------------------------------
        # Normalize
        # ------------------------------------------------------

        audio = self.normalize_audio(
            audio
        )

        # ------------------------------------------------------
        # Final validation
        # ------------------------------------------------------

        self.validate_audio(
            audio,
            self.sample_rate,
        )

        return (
            audio,
            self.sample_rate,
        )


# ==========================================================
# Load and Preprocess File
# ==========================================================

    def load_and_preprocess(
        self,
        audio_path: str,
    ) -> Tuple[np.ndarray, int]:
        """
        Load an audio file and prepare it for
        feature extraction.
        """

        audio, sample_rate = (
            self.load_audio(
                audio_path
            )
        )

        return self.preprocess_audio(
            audio,
            sample_rate,
        )
# ==========================================================
# Pitch + Jitter
# ==========================================================

    def extract_pitch(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Extract:

            MDVP:Fo(Hz)
            MDVP:Fhi(Hz)
            MDVP:Flo(Hz)
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid sample rate."
            )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.size == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        # ------------------------------------------------------
        # Fundamental frequency
        # ------------------------------------------------------

        f0, _, _ = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sample_rate,
        )

        valid_f0 = f0[
            np.isfinite(f0)
        ]

        valid_f0 = valid_f0[
            valid_f0 > 0
        ]

        if len(valid_f0) < 5:
            raise ValueError(
                "Not enough voiced samples detected "
                "for pitch analysis."
            )

        # ------------------------------------------------------
        # Pitch statistics
        # ------------------------------------------------------

        fo = float(
            np.mean(valid_f0)
        )

        fhi = float(
            np.max(valid_f0)
        )

        flo = float(
            np.min(valid_f0)
        )

        values = {
            "MDVP:Fo(Hz)": fo,
            "MDVP:Fhi(Hz)": fhi,
            "MDVP:Flo(Hz)": flo,
        }

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        for name, value in values.items():

            if not np.isfinite(
                value
            ):

                raise ValueError(
                    f"Invalid pitch value for {name}."
                )

        return values


# ==========================================================
# Jitter
# ==========================================================

    def extract_jitter(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Extract:

            MDVP:Jitter(%)
            MDVP:Jitter(Abs)
            MDVP:RAP
            MDVP:PPQ
            Jitter:DDP
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid sample rate."
            )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.size == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        # ------------------------------------------------------
        # Fundamental frequency
        # ------------------------------------------------------

        f0, _, _ = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sample_rate,
        )

        valid_f0 = f0[
            np.isfinite(f0)
        ]

        valid_f0 = valid_f0[
            valid_f0 > 0
        ]

        if len(valid_f0) < 5:
            raise ValueError(
                "Not enough voiced samples detected "
                "for jitter analysis."
            )

        # ------------------------------------------------------
        # Convert frequency to vocal period
        # ------------------------------------------------------

        periods = (
            1.0 / valid_f0
        )

        periods = periods[
            np.isfinite(periods)
            & (periods > 0)
        ]

        if len(periods) < 5:
            raise ValueError(
                "Not enough valid vocal periods."
            )

        mean_period = float(
            np.mean(periods)
        )

        if mean_period <= 0:
            raise ValueError(
                "Invalid mean vocal period."
            )

        # ------------------------------------------------------
        # Absolute period differences
        # ------------------------------------------------------

        period_differences = np.abs(
            np.diff(periods)
        )

        if len(
            period_differences
        ) == 0:

            raise ValueError(
                "Unable to calculate period differences."
            )

        # ------------------------------------------------------
        # MDVP:Jitter(Abs)
        # ------------------------------------------------------

        jitter_abs = float(
            np.mean(
                period_differences
            )
        )

        # ------------------------------------------------------
        # MDVP:Jitter(%)
        # ------------------------------------------------------

        jitter_percent = float(
            jitter_abs
            / mean_period
        )

        # ------------------------------------------------------
        # MDVP:RAP
        # ------------------------------------------------------

        rap_values = []

        for index in range(
            1,
            len(periods) - 1,
        ):

            local_average = (
                periods[index - 1]
                + periods[index]
                + periods[index + 1]
            ) / 3.0

            rap_values.append(
                abs(
                    periods[index]
                    - local_average
                )
            )

        if not rap_values:
            raise ValueError(
                "Unable to calculate RAP."
            )

        rap = float(
            np.mean(
                rap_values
            )
            / mean_period
        )

        # ------------------------------------------------------
        # MDVP:PPQ
        # ------------------------------------------------------

        ppq_values = []

        for index in range(
            2,
            len(periods) - 2,
        ):

            local_average = float(
                np.mean(
                    periods[
                        index - 2:
                        index + 3
                    ]
                )
            )

            ppq_values.append(
                abs(
                    periods[index]
                    - local_average
                )
            )

        if not ppq_values:
            raise ValueError(
                "Unable to calculate PPQ."
            )

        ppq = float(
            np.mean(
                ppq_values
            )
            / mean_period
        )

        # ------------------------------------------------------
        # Jitter:DDP
        # ------------------------------------------------------

        ddp = float(
            rap * 3.0
        )

        # ------------------------------------------------------
        # Final values
        # ------------------------------------------------------

        values = {
            "MDVP:Jitter(%)":
                jitter_percent,

            "MDVP:Jitter(Abs)":
                jitter_abs,

            "MDVP:RAP":
                rap,

            "MDVP:PPQ":
                ppq,

            "Jitter:DDP":
                ddp,
        }

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        for name, value in values.items():

            if not np.isfinite(
                value
            ):

                raise ValueError(
                    f"Invalid jitter value for {name}."
                )

        return values
# ==========================================================
# Shimmer
# ==========================================================

    def extract_shimmer(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Extract:

            MDVP:Shimmer
            MDVP:Shimmer(dB)
            Shimmer:APQ3
            Shimmer:APQ5
            MDVP:APQ
            Shimmer:DDA
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid sample rate."
            )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.size == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        if not np.isfinite(
            audio
        ).all():
            raise ValueError(
                "Audio contains invalid numeric values."
            )

        # ------------------------------------------------------
        # RMS amplitude
        # ------------------------------------------------------

        rms = librosa.feature.rms(
            y=audio,
            frame_length=2048,
            hop_length=512,
        )[0]

        rms = rms[
            np.isfinite(rms)
        ]

        rms = rms[
            rms > 0
        ]

        if len(rms) < 11:
            raise ValueError(
                "Not enough amplitude frames "
                "for shimmer analysis."
            )

        mean_amplitude = float(
            np.mean(rms)
        )

        if mean_amplitude <= 0:
            raise ValueError(
                "Invalid mean amplitude."
            )

        # ------------------------------------------------------
        # MDVP:Shimmer
        # ------------------------------------------------------

        amplitude_differences = np.abs(
            np.diff(rms)
        )

        if len(
            amplitude_differences
        ) == 0:
            raise ValueError(
                "Unable to calculate shimmer."
            )

        shimmer = float(
            np.mean(
                amplitude_differences
            )
            / mean_amplitude
        )

        # ------------------------------------------------------
        # MDVP:Shimmer(dB)
        # ------------------------------------------------------

        amplitude_ratios = (
            rms[1:]
            / rms[:-1]
        )

        amplitude_ratios = (
            amplitude_ratios[
                np.isfinite(
                    amplitude_ratios
                )
                & (
                    amplitude_ratios > 0
                )
            ]
        )

        if len(
            amplitude_ratios
        ) == 0:
            raise ValueError(
                "Unable to calculate shimmer in dB."
            )

        shimmer_db = float(
            np.mean(
                np.abs(
                    20.0
                    * np.log10(
                        amplitude_ratios
                    )
                )
            )
        )

        # ------------------------------------------------------
        # APQ helper
        # ------------------------------------------------------

        def calculate_apq(
            window: int,
        ) -> float:

            if len(rms) < window:
                raise ValueError(
                    f"Not enough amplitude frames "
                    f"for APQ{window}."
                )

            half = window // 2

            values = []

            for index in range(
                half,
                len(rms) - half,
            ):

                local_values = rms[
                    index - half:
                    index + half + 1
                ]

                local_average = float(
                    np.mean(
                        local_values
                    )
                )

                if local_average <= 0:
                    continue

                values.append(
                    abs(
                        rms[index]
                        - local_average
                    )
                    / local_average
                )

            if not values:
                raise ValueError(
                    f"Unable to calculate APQ{window}."
                )

            return float(
                np.mean(values)
            )

        # ------------------------------------------------------
        # Shimmer:APQ3
        # ------------------------------------------------------

        apq3 = calculate_apq(
            3
        )

        # ------------------------------------------------------
        # Shimmer:APQ5
        # ------------------------------------------------------

        apq5 = calculate_apq(
            5
        )

        # ------------------------------------------------------
        # MDVP:APQ
        # ------------------------------------------------------

        apq = calculate_apq(
            11
        )

        # ------------------------------------------------------
        # Shimmer:DDA
        # ------------------------------------------------------

        dda = float(
            apq3 * 3.0
        )

        # ------------------------------------------------------
        # Final values
        # ------------------------------------------------------

        values = {
            "MDVP:Shimmer":
                shimmer,

            "MDVP:Shimmer(dB)":
                shimmer_db,

            "Shimmer:APQ3":
                apq3,

            "Shimmer:APQ5":
                apq5,

            "MDVP:APQ":
                apq,

            "Shimmer:DDA":
                dda,
        }

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        for name, value in values.items():

            if not np.isfinite(
                value
            ):

                raise ValueError(
                    f"Invalid shimmer value for {name}."
                )

        return values


# ==========================================================
# HNR / NHR
# ==========================================================

    def extract_hnr_nhr(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Extract:

            NHR
            HNR
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid sample rate."
            )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.size == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        if not np.isfinite(
            audio
        ).all():
            raise ValueError(
                "Audio contains invalid numeric values."
            )

        # ------------------------------------------------------
        # Harmonic / percussive separation
        # ------------------------------------------------------

        harmonic, percussive = (
            librosa.effects.hpss(
                audio
            )
        )

        harmonic = np.asarray(
            harmonic,
            dtype=np.float64,
        )

        percussive = np.asarray(
            percussive,
            dtype=np.float64,
        )

        # ------------------------------------------------------
        # Harmonic energy
        # ------------------------------------------------------

        harmonic_energy = float(
            np.mean(
                harmonic ** 2
            )
        )

        if not np.isfinite(
            harmonic_energy
        ) or harmonic_energy <= 0:

            raise ValueError(
                "Unable to calculate valid "
                "harmonic energy."
            )

        # ------------------------------------------------------
        # Noise / residual energy
        # ------------------------------------------------------

        residual = (
            audio - harmonic
        )

        noise_energy = float(
            np.mean(
                residual ** 2
            )
        )

        if not np.isfinite(
            noise_energy
        ):

            raise ValueError(
                "Unable to calculate valid "
                "noise energy."
            )

        # Prevent division by zero.

        if noise_energy <= 0:

            noise_energy = (
                np.finfo(
                    np.float64
                ).eps
            )

        # ------------------------------------------------------
        # HNR
        # ------------------------------------------------------

        hnr = float(
            10.0
            * np.log10(
                harmonic_energy
                / noise_energy
            )
        )

        # ------------------------------------------------------
        # NHR
        # ------------------------------------------------------

        nhr = float(
            noise_energy
            / harmonic_energy
        )

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        if not np.isfinite(
            hnr
        ):

            raise ValueError(
                "Calculated HNR is invalid."
            )

        if not np.isfinite(
            nhr
        ):

            raise ValueError(
                "Calculated NHR is invalid."
            )

        return {
            "NHR": nhr,
            "HNR": hnr,
        }
    # ==========================================================
    # RPDE / DFA
    # ==========================================================

    def extract_rpde_dfa(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Extract:

            RPDE
            DFA

        RPDE = Recurrence Period Density Entropy

        DFA = Detrended Fluctuation Analysis
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid sample rate."
            )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.size == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        if not np.isfinite(
            audio
        ).all():
            raise ValueError(
                "Audio contains invalid numeric values."
            )

        # ------------------------------------------------------
        # Remove DC component
        # ------------------------------------------------------

        signal = (
            audio
            - np.mean(audio)
        )

        standard_deviation = float(
            np.std(signal)
        )

        if (
            not np.isfinite(
                standard_deviation
            )
            or standard_deviation <= 0
        ):
            raise ValueError(
                "Audio has insufficient variation "
                "for nonlinear analysis."
            )

        # ------------------------------------------------------
        # Normalize
        # ------------------------------------------------------

        signal = (
            signal
            / standard_deviation
        )

        # ------------------------------------------------------
        # RPDE
        # ------------------------------------------------------

        rpde = self._calculate_rpde(
            signal
        )

        # ------------------------------------------------------
        # DFA
        # ------------------------------------------------------

        dfa = self._calculate_dfa(
            signal
        )

        # ------------------------------------------------------
        # Validate
        # ------------------------------------------------------

        if not np.isfinite(
            rpde
        ):
            raise ValueError(
                "Calculated RPDE is invalid."
            )

        if not np.isfinite(
            dfa
        ):
            raise ValueError(
                "Calculated DFA is invalid."
            )

        return {
            "RPDE": float(
                rpde
            ),
            "DFA": float(
                dfa
            ),
        }


    # ==========================================================
    # RPDE Calculation
    # ==========================================================

    def _calculate_rpde(
        self,
        signal: np.ndarray,
    ) -> float:
        """
        Calculate a recurrence-density entropy measure.
        """

        signal_length = len(
            signal
        )

        if signal_length < 100:
            raise ValueError(
                "Audio signal is too short "
                "for RPDE analysis."
            )

        # ------------------------------------------------------
        # Limit computational size
        # ------------------------------------------------------

        maximum_samples = 20000

        if signal_length > maximum_samples:

            indices = np.linspace(
                0,
                signal_length - 1,
                maximum_samples,
                dtype=int,
            )

            signal = signal[
                indices
            ]

            signal_length = len(
                signal
            )

        # ------------------------------------------------------
        # Center signal
        # ------------------------------------------------------

        signal = (
            signal
            - np.mean(signal)
        )

        denominator = float(
            np.sum(
                signal ** 2
            )
        )

        if denominator <= 0:
            raise ValueError(
                "Unable to calculate RPDE."
            )

        # ------------------------------------------------------
        # Autocorrelation
        # ------------------------------------------------------

        correlation = np.correlate(
            signal,
            signal,
            mode="full",
        )

        correlation = correlation[
            signal_length - 1:
        ]

        correlation = (
            correlation
            / denominator
        )

        # Ignore zero lag.
        correlation = correlation[
            1:
        ]

        correlation = np.abs(
            correlation
        )

        if len(
            correlation
        ) == 0:
            raise ValueError(
                "Unable to construct RPDE profile."
            )

        # ------------------------------------------------------
        # Probability density
        # ------------------------------------------------------

        number_of_bins = 50

        histogram, _ = np.histogram(
            correlation,
            bins=number_of_bins,
            range=(
                0.0,
                1.0,
            ),
        )

        histogram = histogram.astype(
            np.float64
        )

        total = float(
            np.sum(histogram)
        )

        if total <= 0:
            raise ValueError(
                "Unable to calculate RPDE density."
            )

        probability = (
            histogram / total
        )

        probability = probability[
            probability > 0
        ]

        if len(
            probability
        ) == 0:
            raise ValueError(
                "RPDE probability distribution is empty."
            )

        # ------------------------------------------------------
        # Shannon entropy
        # ------------------------------------------------------

        entropy = float(
            -np.sum(
                probability
                * np.log2(
                    probability
                )
            )
        )

        maximum_entropy = np.log2(
            number_of_bins
        )

        if maximum_entropy <= 0:
            raise ValueError(
                "Invalid RPDE entropy normalization."
            )

        return float(
            entropy
            / maximum_entropy
        )
# ==========================================================
# DFA Calculation
# ==========================================================

    def _calculate_dfa(
        self,
        signal: np.ndarray,
    ) -> float:
        """
        Calculate a detrended fluctuation-analysis
        scaling exponent.
        """

        signal_length = len(
            signal
        )

        if signal_length < 100:
            raise ValueError(
                "Audio signal is too short "
                "for DFA analysis."
            )

        # ------------------------------------------------------
        # Integrated profile
        # ------------------------------------------------------

        centered = (
            signal
            - np.mean(signal)
        )

        profile = np.cumsum(
            centered
        )

        # ------------------------------------------------------
        # Window sizes
        # ------------------------------------------------------

        minimum_window = 16

        maximum_window = min(
            signal_length // 4,
            4096,
        )

        if maximum_window <= minimum_window:

            raise ValueError(
                "Audio signal is too short "
                "for DFA window analysis."
            )

        windows = np.unique(
            np.logspace(
                np.log10(
                    minimum_window
                ),
                np.log10(
                    maximum_window
                ),
                num=12,
            ).astype(int)
        )

        valid_windows = []

        fluctuation_sizes = []

        # ------------------------------------------------------
        # Calculate fluctuation for each window
        # ------------------------------------------------------

        for window in windows:

            if window < 4:
                continue

            number_of_segments = (
                len(profile)
                // window
            )

            if number_of_segments < 2:
                continue

            local_fluctuations = []

            for segment_index in range(
                number_of_segments
            ):

                start = (
                    segment_index
                    * window
                )

                end = (
                    start
                    + window
                )

                segment = profile[
                    start:end
                ]

                x = np.arange(
                    window,
                    dtype=np.float64,
                )

                coefficients = np.polyfit(
                    x,
                    segment,
                    1,
                )

                trend = np.polyval(
                    coefficients,
                    x,
                )

                residual = (
                    segment
                    - trend
                )

                fluctuation = np.sqrt(
                    np.mean(
                        residual ** 2
                    )
                )

                if (
                    np.isfinite(
                        fluctuation
                    )
                    and fluctuation > 0
                ):

                    local_fluctuations.append(
                        fluctuation
                    )

            if not local_fluctuations:
                continue

            fluctuation_size = float(
                np.sqrt(
                    np.mean(
                        np.asarray(
                            local_fluctuations
                        ) ** 2
                    )
                )
            )

            if (
                np.isfinite(
                    fluctuation_size
                )
                and fluctuation_size > 0
            ):

                valid_windows.append(
                    window
                )

                fluctuation_sizes.append(
                    fluctuation_size
                )

        # ------------------------------------------------------
        # Validate windows
        # ------------------------------------------------------

        if len(
            valid_windows
        ) < 4:

            raise ValueError(
                "Not enough valid DFA windows."
            )

        # ------------------------------------------------------
        # Log-log regression
        # ------------------------------------------------------

        x_values = np.log10(
            np.asarray(
                valid_windows,
                dtype=np.float64,
            )
        )

        y_values = np.log10(
            np.asarray(
                fluctuation_sizes,
                dtype=np.float64,
            )
        )

        slope, _ = np.polyfit(
            x_values,
            y_values,
            1,
        )

        dfa = float(
            slope
        )

        if not np.isfinite(
            dfa
        ):
            raise ValueError(
                "Calculated DFA is invalid."
            )

        return dfa

    # ==========================================================
    # spread1 / spread2 / D2 / PPE
    # ==========================================================

    def extract_nonlinear_features(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Extract:

            spread1
            spread2
            D2
            PPE
        """

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid sample rate."
            )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        if audio.size == 0:
            raise ValueError(
                "Audio waveform is empty."
            )

        if not np.isfinite(
            audio
        ).all():
            raise ValueError(
                "Audio contains invalid numeric values."
            )

        # ======================================================
        # Fundamental frequency
        # ======================================================

        f0, voiced_flag, _ = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sample_rate,
        )

        valid_f0 = f0[
            np.isfinite(f0)
        ]

        valid_f0 = valid_f0[
            valid_f0 > 0
        ]

        if len(valid_f0) < 20:

            raise ValueError(
                "Not enough voiced samples for "
                "nonlinear feature extraction."
            )

        # ======================================================
        # Log fundamental frequency
        # ======================================================

        log_f0 = np.log(
            valid_f0
        )

        log_f0 = log_f0[
            np.isfinite(log_f0)
        ]

        if len(log_f0) < 20:

            raise ValueError(
                "Invalid logarithmic pitch values."
            )

        # ======================================================
        # spread1
        # ======================================================

        spread1 = float(
            np.std(
                log_f0
            )
        )

        if not np.isfinite(
            spread1
        ):

            raise ValueError(
                "Unable to calculate spread1."
            )

        # ======================================================
        # spread2
        # ======================================================

        differences = np.diff(
            log_f0
        )

        differences = differences[
            np.isfinite(
                differences
            )
        ]

        if len(differences) < 10:

            raise ValueError(
                "Not enough pitch variation for spread2."
            )

        spread2 = float(
            np.std(
                differences
            )
        )

        if not np.isfinite(
            spread2
        ):

            raise ValueError(
                "Unable to calculate spread2."
            )

        # ======================================================
        # PPE — Pitch Period Entropy
        # ======================================================

        periods = (
            1.0
            / valid_f0
        )

        periods = periods[
            np.isfinite(periods)
            & (
                periods > 0
            )
        ]

        if len(periods) < 20:

            raise ValueError(
                "Not enough pitch periods for PPE."
            )

        normalized_periods = (
            periods
            / np.mean(periods)
        )

        # ------------------------------------------------------
        # Remove extreme numerical values
        # ------------------------------------------------------

        normalized_periods = (
            normalized_periods[
                np.isfinite(
                    normalized_periods
                )
            ]
        )

        if len(
            normalized_periods
        ) < 20:

            raise ValueError(
                "Invalid normalized pitch periods."
            )

        # ------------------------------------------------------
        # Histogram probability
        # ------------------------------------------------------

        number_of_bins = 50

        histogram, _ = np.histogram(
            normalized_periods,
            bins=number_of_bins,
        )

        histogram = histogram.astype(
            np.float64
        )

        histogram_total = float(
            np.sum(
                histogram
            )
        )

        if histogram_total <= 0:

            raise ValueError(
                "Unable to calculate PPE distribution."
            )

        probability = (
            histogram
            / histogram_total
        )

        probability = probability[
            probability > 0
        ]

        if len(probability) == 0:

            raise ValueError(
                "PPE probability distribution is empty."
            )

        entropy = float(
            -np.sum(
                probability
                * np.log2(
                    probability
                )
            )
        )

        maximum_entropy = np.log2(
            number_of_bins
        )

        if maximum_entropy <= 0:

            raise ValueError(
                "Invalid PPE entropy normalization."
            )

        ppe = float(
            entropy
            / maximum_entropy
        )

        # ======================================================
        # D2 — Correlation Dimension
        # ======================================================

        d2 = self._calculate_d2(
            log_f0
        )

        # ======================================================
        # Validate
        # ======================================================

        values = {
            "spread1":
                spread1,

            "spread2":
                spread2,

            "D2":
                d2,

            "PPE":
                ppe,
        }

        for name, value in values.items():

            if not np.isfinite(
                value
            ):

                raise ValueError(
                    f"Invalid nonlinear feature: {name}"
                )

        return values


    # ==========================================================
    # D2 Calculation
    # ==========================================================

    def _calculate_d2(
        self,
        signal: np.ndarray,
    ) -> float:
        """
        Estimate the correlation dimension using a
        delay-embedded signal and correlation integral.
        """

        signal = np.asarray(
            signal,
            dtype=np.float64,
        )

        signal = signal[
            np.isfinite(signal)
        ]

        if len(signal) < 100:

            raise ValueError(
                "Signal is too short for D2 analysis."
            )

        # ------------------------------------------------------
        # Limit computation
        # ------------------------------------------------------

        maximum_samples = 2000

        if len(signal) > maximum_samples:

            indices = np.linspace(
                0,
                len(signal) - 1,
                maximum_samples,
                dtype=int,
            )

            signal = signal[
                indices
            ]

        # ------------------------------------------------------
        # Normalize
        # ------------------------------------------------------

        signal = (
            signal
            - np.mean(signal)
        )

        standard_deviation = float(
            np.std(signal)
        )

        if standard_deviation <= 0:

            raise ValueError(
                "Insufficient variation for D2."
            )

        signal = (
            signal
            / standard_deviation
        )

        # ------------------------------------------------------
        # Delay embedding
        # ------------------------------------------------------

        embedding_dimension = 3

        delay = 1

        number_of_vectors = (
            len(signal)
            - (
                embedding_dimension
                - 1
            )
            * delay
        )

        if number_of_vectors < 50:

            raise ValueError(
                "Not enough embedded vectors for D2."
            )

        embedded = np.empty(
            (
                number_of_vectors,
                embedding_dimension,
            ),
            dtype=np.float64,
        )

        for dimension in range(
            embedding_dimension
        ):

            start = (
                dimension
                * delay
            )

            end = (
                start
                + number_of_vectors
            )

            embedded[
                :,
                dimension
            ] = signal[
                start:end
            ]

        # ------------------------------------------------------
        # Pairwise distances
        # ------------------------------------------------------

        distances = []

        block_size = 500

        for start in range(
            0,
            len(embedded),
            block_size,
        ):

            block = embedded[
                start:
                start + block_size
            ]

            difference = (
                block[:, None, :]
                - embedded[None, :, :]
            )

            block_distances = np.sqrt(
                np.sum(
                    difference ** 2,
                    axis=2,
                )
            )

            # Remove self-distances.
            block_distances[
                np.arange(
                    len(block)
                ),
                np.arange(
                    start,
                    min(
                        start
                        + len(block),
                        len(embedded),
                    ),
                )
            ] = np.nan

            valid_distances = (
                block_distances[
                    np.isfinite(
                        block_distances
                    )
                ]
            )

            if len(
                valid_distances
            ) > 0:

                distances.append(
                    valid_distances
                )

        if not distances:

            raise ValueError(
                "Unable to calculate D2 distances."
            )

        distances = np.concatenate(
            distances
        )

        distances = distances[
            distances > 0
        ]

        if len(distances) < 100:

            raise ValueError(
                "Not enough valid distances for D2."
            )

        # ------------------------------------------------------
        # Radius range
        # ------------------------------------------------------

        low_radius = float(
            np.percentile(
                distances,
                10,
            )
        )

        high_radius = float(
            np.percentile(
                distances,
                60,
            )
        )

        if (
            low_radius <= 0
            or high_radius <= low_radius
        ):

            raise ValueError(
                "Invalid D2 radius range."
            )

        radii = np.logspace(
            np.log10(
                low_radius
            ),
            np.log10(
                high_radius
            ),
            12,
        )

        correlation_values = []

        valid_radii = []

        total_pairs = float(
            len(distances)
        )

        for radius in radii:

            count = float(
                np.sum(
                    distances < radius
                )
            )

            if count <= 0:
                continue

            correlation = (
                count
                / total_pairs
            )

            if (
                correlation > 0
                and np.isfinite(
                    correlation
                )
            ):

                valid_radii.append(
                    radius
                )

                correlation_values.append(
                    correlation
                )

        if len(
            valid_radii
        ) < 4:

            raise ValueError(
                "Not enough valid scales for D2."
            )

        # ------------------------------------------------------
        # Log-log regression
        # ------------------------------------------------------

        log_radii = np.log(
            np.asarray(
                valid_radii,
                dtype=np.float64,
            )
        )

        log_correlations = np.log(
            np.asarray(
                correlation_values,
                dtype=np.float64,
            )
        )

        slope, _ = np.polyfit(
            log_radii,
            log_correlations,
            1,
        )

        d2 = float(
            slope
        )

        if not np.isfinite(
            d2
        ):

            raise ValueError(
                "Calculated D2 is invalid."
            )

        return d2


    # ==========================================================
    # Assemble and Validate All 22 Features
    # ==========================================================

    def assemble_features(
        self,
        pitch_features: dict,
        jitter_features: dict,
        shimmer_features: dict,
        hnr_features: dict,
        nonlinear_features: dict,
        rpde_dfa_features: dict,
    ) -> dict:
        """
        Combine all extracted feature groups into the exact
        22-feature dictionary expected by the Parkinson model.
        """

        feature_groups = [
            pitch_features,
            jitter_features,
            shimmer_features,
            hnr_features,
            rpde_dfa_features,
            nonlinear_features,
        ]

        combined = {}

        # ------------------------------------------------------
        # Combine feature groups
        # ------------------------------------------------------

        for group in feature_groups:

            if not isinstance(
                group,
                dict,
            ):

                raise ValueError(
                    "Every feature group must be a dictionary."
                )

            for name, value in group.items():

                if name in combined:

                    raise ValueError(
                        f"Duplicate feature detected: {name}"
                    )

                combined[name] = value

        # ------------------------------------------------------
        # Check missing features
        # ------------------------------------------------------

        missing_features = [
            name
            for name in FEATURE_NAMES
            if name not in combined
        ]

        if missing_features:

            raise ValueError(
                "Missing model features: "
                f"{missing_features}"
            )

        # ------------------------------------------------------
        # Check unexpected features
        # ------------------------------------------------------

        unexpected_features = [
            name
            for name in combined
            if name not in FEATURE_NAMES
        ]

        if unexpected_features:

            raise ValueError(
                "Unexpected model features: "
                f"{unexpected_features}"
            )

        # ------------------------------------------------------
        # Build exact model order
        # ------------------------------------------------------

        ordered_features = {}

        for name in FEATURE_NAMES:

            try:

                value = float(
                    combined[name]
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Feature '{name}' must be numeric."
                ) from exc

            if not np.isfinite(
                value
            ):

                raise ValueError(
                    f"Feature '{name}' contains "
                    "an invalid numeric value."
                )

            ordered_features[
                name
            ] = value

        # ------------------------------------------------------
        # Final count
        # ------------------------------------------------------

        if len(
            ordered_features
        ) != TOTAL_FEATURES:

            raise ValueError(
                "Invalid feature count. "
                f"Expected {TOTAL_FEATURES}, "
                f"received {len(ordered_features)}."
            )

        return ordered_features


    # ==========================================================
    # Validate Feature Dictionary
    # ==========================================================

    def validate_feature_dictionary(
        self,
        features: dict,
    ) -> bool:
        """
        Verify that a feature dictionary contains exactly
        the 22 model features.
        """

        if not isinstance(
            features,
            dict,
        ):

            raise ValueError(
                "Features must be provided as a dictionary."
            )

        if len(
            features
        ) != TOTAL_FEATURES:

            raise ValueError(
                "Expected exactly "
                f"{TOTAL_FEATURES} features, "
                f"received {len(features)}."
            )

        # ------------------------------------------------------
        # Missing
        # ------------------------------------------------------

        missing = [
            name
            for name in FEATURE_NAMES
            if name not in features
        ]

        if missing:

            raise ValueError(
                "Missing features: "
                f"{missing}"
            )

        # ------------------------------------------------------
        # Unexpected
        # ------------------------------------------------------

        unexpected = [
            name
            for name in features
            if name not in FEATURE_NAMES
        ]

        if unexpected:

            raise ValueError(
                "Unexpected features: "
                f"{unexpected}"
            )

        # ------------------------------------------------------
        # Numeric validation
        # ------------------------------------------------------

        for name in FEATURE_NAMES:

            try:

                value = float(
                    features[name]
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Feature '{name}' must be numeric."
                ) from exc

            if not np.isfinite(
                value
            ):

                raise ValueError(
                    f"Feature '{name}' contains "
                    "an invalid numeric value."
                )

        return True


    # ==========================================================
    # Get Ordered Feature Names
    # ==========================================================

    def get_feature_names(
        self,
    ) -> List[str]:
        """
        Return the exact 22-feature order expected by
        the trained model.
        """

        return FEATURE_NAMES.copy()


    # ==========================================================
    # Feature Count
    # ==========================================================

    def get_feature_count(
        self,
    ) -> int:
        """
        Return the total number of model features.
        """

        return TOTAL_FEATURES

    # ==========================================================
    # Model-Ready 22 Feature Vector
    # ==========================================================

    def to_feature_vector(
        self,
        features: dict,
    ) -> List[float]:
        """
        Convert the validated feature dictionary into the
        exact 22-value order expected by model.pkl.
        """

        self.validate_feature_dictionary(
            features
        )

        vector = []

        for feature_name in FEATURE_NAMES:

            try:

                value = float(
                    features[
                        feature_name
                    ]
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Feature '{feature_name}' "
                    "must be numeric."
                ) from exc

            if not np.isfinite(
                value
            ):

                raise ValueError(
                    f"Feature '{feature_name}' "
                    "contains an invalid value."
                )

            vector.append(
                value
            )

        if len(vector) != TOTAL_FEATURES:

            raise ValueError(
                "Invalid model feature vector. "
                f"Expected {TOTAL_FEATURES} values, "
                f"received {len(vector)}."
            )

        return vector


    # ==========================================================
    # NumPy Model Input
    # ==========================================================

    def to_numpy_vector(
        self,
        features: dict,
    ) -> np.ndarray:
        """
        Convert the validated 22-feature vector into
        shape (1, 22), ready for the existing scaler.
        """

        vector = self.to_feature_vector(
            features
        )

        data = np.asarray(
            vector,
            dtype=np.float64,
        )

        if data.shape != (
            TOTAL_FEATURES,
        ):

            raise ValueError(
                "Invalid feature array shape: "
                f"{data.shape}"
            )

        model_input = data.reshape(
            1,
            TOTAL_FEATURES,
        )

        self.validate_model_input(
            model_input
        )

        return model_input


    # ==========================================================
    # Validate Model Input
    # ==========================================================

    def validate_model_input(
        self,
        data: np.ndarray,
    ) -> bool:
        """
        Validate the final NumPy array before it is passed
        to preprocessing.py and the trained model.
        """

        if not isinstance(
            data,
            np.ndarray,
        ):

            raise ValueError(
                "Model input must be a NumPy array."
            )

        if data.shape != (
            1,
            TOTAL_FEATURES,
        ):

            raise ValueError(
                "Model input must have shape "
                f"(1, {TOTAL_FEATURES}). "
                f"Received {data.shape}."
            )

        if data.dtype.kind not in (
            "f",
            "i",
            "u",
        ):

            raise ValueError(
                "Model input must contain numeric values."
            )

        if not np.isfinite(
            data
        ).all():

            raise ValueError(
                "Model input contains invalid values."
            )

        return True


    # ==========================================================
    # Feature Summary
    # ==========================================================

    def feature_summary(
        self,
        features: dict,
    ) -> List[dict]:
        """
        Return all 22 features with their index, name,
        and calculated value.
        """

        self.validate_feature_dictionary(
            features
        )

        summary = []

        for index, feature_name in enumerate(
            FEATURE_NAMES,
            start=1,
        ):

            summary.append(
                {
                    "index": index,
                    "feature": feature_name,
                    "value": float(
                        features[
                            feature_name
                        ]
                    ),
                }
            )

        return summary


    # ==========================================================
    # Extract All Features
    # ==========================================================

    def extract_features(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:
        """
        Run the complete audio feature extraction pipeline.

        Returns exactly 22 named features.
        """

        # ------------------------------------------------------
        # Preprocess
        # ------------------------------------------------------

        processed_audio, processed_rate = (
            self.preprocess_audio(
                audio,
                sample_rate,
            )
        )

        # ------------------------------------------------------
        # Extract feature groups
        # ------------------------------------------------------

        pitch_features = (
            self.extract_pitch(
                processed_audio,
                processed_rate,
            )
        )

        jitter_features = (
            self.extract_jitter(
                processed_audio,
                processed_rate,
            )
        )

        shimmer_features = (
            self.extract_shimmer(
                processed_audio,
                processed_rate,
            )
        )

        hnr_features = (
            self.extract_hnr_nhr(
                processed_audio,
                processed_rate,
            )
        )

        rpde_dfa_features = (
            self.extract_rpde_dfa(
                processed_audio,
                processed_rate,
            )
        )

        nonlinear_features = (
            self.extract_nonlinear_features(
                processed_audio,
                processed_rate,
            )
        )

        # ------------------------------------------------------
        # Assemble all 22 features
        # ------------------------------------------------------

        features = self.assemble_features(
            pitch_features,
            jitter_features,
            shimmer_features,
            hnr_features,
            nonlinear_features,
            rpde_dfa_features,
        )

        # ------------------------------------------------------
        # Final validation
        # ------------------------------------------------------

        self.validate_feature_dictionary(
            features
        )

        return features



# ==========================================================
# Extract From File
# ==========================================================

    def extract_features_from_file(
        self,
        audio_path: str,
    ) -> dict:
        """
        Load an audio file and extract the complete
        22-feature representation.
        """

        audio, sample_rate = (
            self.load_and_preprocess(
                audio_path
            )
        )

        # The audio returned by
        # load_and_preprocess() is already
        # preprocessed, so call the individual
        # extractors directly.

        pitch_features = (
            self.extract_pitch(
                audio,
                sample_rate,
            )
        )

        jitter_features = (
            self.extract_jitter(
                audio,
                sample_rate,
            )
        )

        shimmer_features = (
            self.extract_shimmer(
                audio,
                sample_rate,
            )
        )

        hnr_features = (
            self.extract_hnr_nhr(
                audio,
                sample_rate,
            )
        )

        rpde_dfa_features = (
            self.extract_rpde_dfa(
                audio,
                sample_rate,
            )
        )

        nonlinear_features = (
            self.extract_nonlinear_features(
                audio,
                sample_rate,
            )
        )

        features = self.assemble_features(
            pitch_features,
            jitter_features,
            shimmer_features,
            hnr_features,
            nonlinear_features,
            rpde_dfa_features,
        )

        self.validate_feature_dictionary(
            features
        )

        return features


# ==========================================================
# Extract Model Vector From File
# ==========================================================

    def extract_model_vector_from_file(
        self,
        audio_path: str,
    ) -> np.ndarray:
        """
        Load an audio file, extract all 22 features, and
        return a NumPy array with shape (1, 22).

        This array can be passed to the existing
        Preprocessor.scale() method.
        """

        features = (
            self.extract_features_from_file(
                audio_path
            )
        )

        return self.to_numpy_vector(
            features
        )


# ==========================================================
# Shared Service Instance
# ==========================================================

audio_feature_service = (
    AudioFeatureService()
)
