from pathlib import Path
from typing import Union, Tuple

import librosa
import numpy as np


# ==========================================================
# Total Model Features
# ==========================================================

TOTAL_FEATURES = 22


# ==========================================================
# 22 Model Feature Names
# ==========================================================

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


# ==========================================================
# Validate Feature Definition
# ==========================================================

if len(FEATURE_NAMES) != TOTAL_FEATURES:
    raise ValueError(
        "FEATURE_NAMES must contain exactly "
        f"{TOTAL_FEATURES} features."
    )


# ==========================================================
# Audio Feature Service
# ==========================================================

class AudioFeatureService:

    SAMPLE_RATE = 22050

    MIN_DURATION_SECONDS = 1.0

    MAX_DURATION_SECONDS = 60.0

    SUPPORTED_EXTENSIONS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
    }


    # ======================================================
    # Load Audio
    # ======================================================

    def load_audio(
        self,
        audio_path: Union[str, Path],
    ) -> Tuple[np.ndarray, int]:

        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Audio path is not a file: {path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported audio format. "
                "Supported formats are WAV, MP3, "
                "M4A, FLAC, and OGG."
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

        self.validate_audio(
            audio,
            sample_rate,
        )

        return audio, sample_rate


    # ======================================================
    # Validate Audio
    # ======================================================

    def validate_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> None:

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        if not isinstance(
            audio,
            np.ndarray,
        ):
            raise ValueError(
                "Invalid audio waveform."
            )

        if audio.size == 0:
            raise ValueError(
                "Audio file contains no samples."
            )

        if sample_rate <= 0:
            raise ValueError(
                "Invalid audio sample rate."
            )

        if not np.isfinite(audio).all():
            raise ValueError(
                "Audio contains invalid numeric values."
            )

        duration = (
            len(audio)
            / float(sample_rate)
        )

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

        peak = float(
            np.max(
                np.abs(audio)
            )
        )

        if peak <= 0:
            raise ValueError(
                "Audio recording is silent."
            )


    # ======================================================
    # Remove DC Offset
    # ======================================================

    def remove_dc_offset(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:

        if audio is None:
            raise ValueError(
                "Audio waveform is missing."
            )

        return (
            audio
            - np.mean(audio)
        )


    # ======================================================
    # Normalize Audio
    # ======================================================

    def normalize_audio(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:

        peak = float(
            np.max(
                np.abs(audio)
            )
        )

        if peak <= 0:
            raise ValueError(
                "Cannot normalize silent audio."
            )

        return (
            audio / peak
        ).astype(
            np.float64
        )


    # ======================================================
    # Preprocess Audio
    # ======================================================

    def preprocess_audio(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:

        audio = self.remove_dc_offset(
            audio
        )

        audio = self.normalize_audio(
            audio
        )

        return audio


    # ======================================================
    # Audio Information
    # ======================================================

    def audio_information(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> dict:

        self.validate_audio(
            audio,
            sample_rate,
        )

        duration = (
            len(audio)
            / float(sample_rate)
        )

        return {
            "sample_rate": int(
                sample_rate
            ),
            "samples": int(
                len(audio)
            ),
            "duration_seconds": round(
                duration,
                3,
            ),
            "channels": 1,
            "format": "mono",
        }


# ==========================================================
# Shared Audio Service
# ==========================================================

audio_feature_service = (
    AudioFeatureService()
)

# ==========================================================
#  Pitch
# ==========================================================

def extract_pitch(
    self,
    audio: np.ndarray,
    sample_rate: int,
) -> dict:
    """
    Extract the three fundamental-frequency features.
    """

    if audio is None:
        raise ValueError(
            "Audio waveform is missing."
        )

    f0, voiced_flag, voiced_prob = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sample_rate,
    )

    valid_f0 = f0[
        np.isfinite(f0)
    ]

    if len(valid_f0) < 3:
        raise ValueError(
            "Unable to detect enough voiced "
            "segments for pitch analysis."
        )

    return {
        "MDVP:Fo(Hz)": float(
            np.mean(valid_f0)
        ),
        "MDVP:Fhi(Hz)": float(
            np.max(valid_f0)
        ),
        "MDVP:Flo(Hz)": float(
            np.min(valid_f0)
        ),
    }

# ==========================================================
# Jitter
# ==========================================================

def extract_jitter(
    self,
    audio: np.ndarray,
    sample_rate: int,
) -> dict:
    """
    Extract jitter-related voice features.

    Features:
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

    if len(valid_f0) < 5:
        raise ValueError(
            "Not enough voiced samples detected "
            "for jitter analysis."
        )

    # ------------------------------------------------------
    # Convert frequency to period
    # ------------------------------------------------------

    periods = 1.0 / valid_f0

    periods = periods[
        np.isfinite(periods)
        & (periods > 0)
    ]

    if len(periods) < 5:
        raise ValueError(
            "Not enough valid vocal periods "
            "for jitter analysis."
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

    differences = np.abs(
        np.diff(periods)
    )

    if len(differences) == 0:
        raise ValueError(
            "Unable to calculate period differences."
        )

    # ------------------------------------------------------
    # MDVP:Jitter(Abs)
    # ------------------------------------------------------

    jitter_absolute = float(
        np.mean(differences)
    )

    # ------------------------------------------------------
    # MDVP:Jitter(%)
    # ------------------------------------------------------

    jitter_percent = float(
        jitter_absolute
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
        np.mean(rap_values)
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
        np.mean(ppq_values)
        / mean_period
    )

    # ------------------------------------------------------
    # Jitter:DDP
    # ------------------------------------------------------

    ddp = float(
        rap * 3.0
    )

    # ------------------------------------------------------
    # Validate results
    # ------------------------------------------------------

    values = {
        "MDVP:Jitter(%)":
            jitter_percent,

        "MDVP:Jitter(Abs)":
            jitter_absolute,

        "MDVP:RAP":
            rap,

        "MDVP:PPQ":
            ppq,

        "Jitter:DDP":
            ddp,
    }

    for name, value in values.items():

        if not np.isfinite(value):

            raise ValueError(
                f"Invalid calculated value "
                f"for {name}."
            )

    return values

# ==========================================================
# Shimmer
# ==========================================================

def extract_shimmer(
    self,
    audio: np.ndarray,
) -> dict:
    """
    Extract shimmer-related voice features.

    Features:
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

    if len(amplitude_ratios) == 0:
        raise ValueError(
            "Unable to calculate "
            "shimmer in dB."
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
    # APQ calculation helper
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
                f"Unable to calculate "
                f"APQ{window}."
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
    # Final validation
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

    for name, value in values.items():

        if not np.isfinite(
            value
        ):

            raise ValueError(
                f"Invalid calculated value "
                f"for {name}."
            )

    return values

# ==========================================================
# HNR / NHR
# ==========================================================

def extract_hnr_nhr(
    self,
    audio: np.ndarray,
) -> dict:
    """
    Extract Harmonics-to-Noise Ratio and
    Noise-to-Harmonics Ratio.

    Features:
        NHR
        HNR
    """

    if audio is None:
        raise ValueError(
            "Audio waveform is missing."
        )

    if audio.size == 0:
        raise ValueError(
            "Audio waveform is empty."
        )

    # ------------------------------------------------------
    # Harmonic / percussive decomposition
    # ------------------------------------------------------

    harmonic, percussive = (
        librosa.effects.hpss(
            audio
        )
    )

    # ------------------------------------------------------
    # Calculate harmonic energy
    # ------------------------------------------------------

    harmonic_energy = float(
        np.mean(
            harmonic ** 2
        )
    )

    if (
        not np.isfinite(
            harmonic_energy
        )
        or harmonic_energy <= 0
    ):
        raise ValueError(
            "Unable to calculate valid "
            "harmonic energy."
        )

    # ------------------------------------------------------
    # Calculate residual/noise energy
    # ------------------------------------------------------

    noise = (
        audio - harmonic
    )

    noise_energy = float(
        np.mean(
            noise ** 2
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
        noise_energy = np.finfo(
            np.float64
        ).eps

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

    if audio.size == 0:
        raise ValueError(
            "Audio waveform is empty."
        )

    audio = np.asarray(
        audio,
        dtype=np.float64,
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

    # ------------------------------------------------------
    # Normalize
    # ------------------------------------------------------

    standard_deviation = float(
        np.std(signal)
    )

    if standard_deviation <= 0:
        raise ValueError(
            "Audio has insufficient variation "
            "for nonlinear analysis."
        )

    signal = (
        signal
        / standard_deviation
    )

    # ======================================================
    # RPDE
    # ======================================================

    # Use the normalized signal to estimate
    # recurrence-density behavior.

    rpde = self._calculate_rpde(
        signal
    )

    # ======================================================
    # DFA
    # ======================================================

    dfa = self._calculate_dfa(
        signal
    )

    # ======================================================
    # Validate
    # ======================================================

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
    Estimate Recurrence Period Density Entropy.

    The calculation uses a normalized autocorrelation
    recurrence profile and entropy measurement.
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
    # Limit computation size
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
    # Autocorrelation
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

    # ------------------------------------------------------
    # Ignore zero lag
    # ------------------------------------------------------

    correlation = correlation[
        1:
    ]

    correlation = np.abs(
        correlation
    )

    if len(correlation) == 0:
        raise ValueError(
            "Unable to construct RPDE recurrence profile."
        )

    # ------------------------------------------------------
    # Convert recurrence profile to density
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

    if len(probability) == 0:
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

    # ------------------------------------------------------
    # Normalize entropy
    # ------------------------------------------------------

    maximum_entropy = np.log2(
        number_of_bins
    )

    if maximum_entropy <= 0:
        raise ValueError(
            "Invalid RPDE entropy normalization."
        )

    rpde = (
        entropy
        / maximum_entropy
    )

    return float(
        rpde
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
    # Integrate the signal
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

    fluctuation_sizes = []

    valid_windows = []

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

            if np.isfinite(
                fluctuation
            ) and fluctuation > 0:

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
    # Validate
    # ------------------------------------------------------

    if len(
        valid_windows
    ) < 4:

        raise ValueError(
            "Not enough valid DFA windows."
        )

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

    # ------------------------------------------------------
    # Scaling exponent
    # ------------------------------------------------------

    slope, _ = np.polyfit(
        x_values,
        y_values,
        1,
    )

    dfa = float(
        slope
    )

    return dfa

# ==========================================================
# spread1 / spread2
# ==========================================================

def extract_spread_features(
    self,
    audio: np.ndarray,
    sample_rate: int,
) -> dict:
    """
    Extract:

        spread1
        spread2

    These two features are part of the 22-feature
    Parkinson dataset but their exact raw-audio
    extraction methodology is not defined in the
    current project source.

    They must not be replaced with arbitrary
    approximations because the resulting values
    would not necessarily match the distribution
    used to train model.pkl.
    """

    if audio is None:
        raise ValueError(
            "Audio waveform is missing."
        )

    if audio.size == 0:
        raise ValueError(
            "Audio waveform is empty."
        )

    if sample_rate <= 0:
        raise ValueError(
            "Invalid sample rate."
        )

    raise NotImplementedError(
        "spread1 and spread2 extraction requires "
        "the original feature-extraction methodology "
        "used to create parkinsons.csv."
    )

# ==========================================================
# D2 / PPE
# ==========================================================

def extract_d2_ppe(
    self,
    audio: np.ndarray,
    sample_rate: int,
) -> dict:
    """
    Extract:

        D2
        PPE

    D2  = correlation dimension
    PPE = pitch period entropy

    The exact extraction methodology used to generate
    these features in the training dataset is not
    currently defined in this project source.

    Do not substitute arbitrary approximations because
    the resulting values may not match the distribution
    used to train model.pkl.
    """

    if audio is None:
        raise ValueError(
            "Audio waveform is missing."
        )

    if audio.size == 0:
        raise ValueError(
            "Audio waveform is empty."
        )

    if sample_rate <= 0:
        raise ValueError(
            "Invalid sample rate."
        )

    raise NotImplementedError(
        "D2 and PPE extraction requires the original "
        "feature-extraction methodology used to create "
        "parkinsons.csv."
    )

# ==========================================================
# 3I — Assemble and Validate 22 Features
# ==========================================================

def assemble_features(
    self,
    feature_groups: list,
) -> dict:
    """
    Combine all extracted feature groups.

    The final result must contain exactly the 22
    features expected by model.pkl.
    """

    if not isinstance(
        feature_groups,
        list,
    ):
        raise ValueError(
            "feature_groups must be a list."
        )

    features = {}

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

            if name in features:
                raise ValueError(
                    f"Duplicate feature detected: {name}"
                )

            features[name] = value

    # ------------------------------------------------------
    # Check missing features
    # ------------------------------------------------------

    missing_features = [
        name
        for name in FEATURE_NAMES
        if name not in features
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
        for name in features
        if name not in FEATURE_NAMES
    ]

    if unexpected_features:

        raise ValueError(
            "Unexpected model features: "
            f"{unexpected_features}"
        )

    # ------------------------------------------------------
    # Create exact feature order
    # ------------------------------------------------------

    ordered_features = {}

    for name in FEATURE_NAMES:

        value = features[name]

        try:

            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Feature '{name}' is not numeric."
            ) from exc

        if not np.isfinite(
            numeric_value
        ):

            raise ValueError(
                f"Feature '{name}' contains "
                "an invalid numeric value."
            )

        ordered_features[
            name
        ] = numeric_value

    # ------------------------------------------------------
    # Final feature count
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
# Feature Dictionary Validation
# ==========================================================

def validate_feature_dictionary(
    self,
    features: dict,
) -> bool:
    """
    Verify that a feature dictionary contains the
    exact 22 model features in the correct structure.
    """

    if not isinstance(
        features,
        dict,
    ):
        raise ValueError(
            "Features must be provided as a dictionary."
        )

    if len(features) != TOTAL_FEATURES:

        raise ValueError(
            "Expected exactly "
            f"{TOTAL_FEATURES} features, "
            f"received {len(features)}."
        )

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
                "an invalid value."
            )

    return True


# ==========================================================
# 3I — Get Ordered Feature Names
# ==========================================================

def get_feature_names(
    self,
) -> list:
    """
    Return the exact feature order expected by
    model.pkl.
    """

    return FEATURE_NAMES.copy()


# ==========================================================
# 3I — Get Feature Count
# ==========================================================

def get_feature_count(
    self,
) -> int:
    """
    Return the number of model features.
    """

    return TOTAL_FEATURES

# ==========================================================
# 3J — Model-Ready 22 Feature Vector
# ==========================================================

def to_feature_vector(
    self,
    features: dict,
) -> list:
    """
    Convert the validated feature dictionary into
    the exact 22-value order expected by model.pkl.
    """

    if not isinstance(
        features,
        dict,
    ):
        raise ValueError(
            "Features must be provided as a dictionary."
        )

    # ------------------------------------------------------
    # Validate exact feature set
    # ------------------------------------------------------

    self.validate_feature_dictionary(
        features
    )

    # ------------------------------------------------------
    # Build vector in training order
    # ------------------------------------------------------

    vector = []

    for feature_name in FEATURE_NAMES:

        value = features[
            feature_name
        ]

        try:

            value = float(
                value
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

    # ------------------------------------------------------
    # Final count validation
    # ------------------------------------------------------

    if len(vector) != TOTAL_FEATURES:

        raise ValueError(
            "Invalid model feature vector. "
            f"Expected {TOTAL_FEATURES} values, "
            f"received {len(vector)}."
        )

    return vector


# ==========================================================
# 3J — NumPy Model Input
# ==========================================================

def to_numpy_vector(
    self,
    features: dict,
) -> np.ndarray:
    """
    Convert the validated 22-feature vector into
    the shape expected by scikit-learn.
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

    return data.reshape(
        1,
        TOTAL_FEATURES,
    )


# ==========================================================
# 3J — Model Input Validation
# ==========================================================

def validate_model_input(
    self,
    data: np.ndarray,
) -> bool:
    """
    Validate the final model input before it is sent
    to the scaler/model.
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
) -> list:
    """
    Return the 22 features with their names and
    values for debugging and verification.
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
