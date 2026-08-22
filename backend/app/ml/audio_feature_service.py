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

FMIN_HZ = 60.0
FMAX_HZ = 600.0

MAX_NONLINEAR_SAMPLES = 12000


# ==========================================================
# Feature Names
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
    Extract the 22 voice features used by the
    Parkinson prediction pipeline.

    Important compatibility methods:

        extract_features()
        extract_features_from_file()
        feature_vector()
        to_feature_vector()

    The to_feature_vector() method is intentionally retained
    because prediction_service.py expects that method.
    """

    TOTAL_FEATURES = TOTAL_FEATURES

    FEATURE_NAMES = FEATURE_NAMES.copy()

    DEFAULT_SAMPLE_RATE = DEFAULT_SAMPLE_RATE

    MIN_DURATION_SECONDS = MIN_DURATION_SECONDS

    MAX_DURATION_SECONDS = MAX_DURATION_SECONDS

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        min_duration: float = MIN_DURATION_SECONDS,
        max_duration: float = MAX_DURATION_SECONDS,
    ):

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

    def get_feature_count(self) -> int:

        return TOTAL_FEATURES

    # ======================================================
    # Feature Names
    # ======================================================

    def get_feature_names(
        self,
    ) -> List[str]:

        return FEATURE_NAMES.copy()

    # ======================================================
    # Load Audio
    # ======================================================

    def load_audio(
        self,
        audio_path: str,
    ) -> Tuple[np.ndarray, int]:

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

            audio, sample_rate = (
                sf.read(
                    str(path),
                    dtype="float64",
                    always_2d=False,
                )
            )

        except Exception as exc:

            raise ValueError(
                f"Unable to read audio file: {path}"
            ) from exc

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        # --------------------------------------------------
        # Convert stereo to mono
        # --------------------------------------------------

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

        return (
            audio,
            sample_rate,
        )

    # ======================================================
    # Validate Audio
    # ======================================================

    def validate_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> bool:

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

    # ======================================================
    # Remove DC Offset
    # ======================================================

    def remove_dc_offset(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:

        return (
            audio
            - np.mean(audio)
        )

    # ======================================================
    # Normalize
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

            return audio

        return (
            audio
            / peak
        )

    # ======================================================
    # Resample
    # ======================================================

    def resample_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:

        if sample_rate <= 0:

            raise ValueError(
                "Invalid source sample rate."
            )

        if sample_rate == self.sample_rate:

            return np.asarray(
                audio,
                dtype=np.float64,
            )

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

    # ======================================================
    # Preprocess
    # ======================================================

    def preprocess_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> Tuple[np.ndarray, int]:

        self.validate_audio(
            audio,
            sample_rate,
        )

        audio = np.asarray(
            audio,
            dtype=np.float64,
        )

        # --------------------------------------------------
        # Mono
        # --------------------------------------------------

        if audio.ndim == 2:

            audio = np.mean(
                audio,
                axis=1,
            )

        elif audio.ndim != 1:

            raise ValueError(
                "Audio must be mono or multi-channel."
            )

        # --------------------------------------------------
        # Remove DC offset
        # --------------------------------------------------

        audio = self.remove_dc_offset(
            audio
        )

        # --------------------------------------------------
        # Resample
        # --------------------------------------------------

        audio = self.resample_audio(
            audio,
            sample_rate,
        )

        # --------------------------------------------------
        # Normalize
        # --------------------------------------------------

        audio = self.normalize_audio(
            audio
        )

        self.validate_audio(
            audio,
            self.sample_rate,
        )

        return (
            audio,
            self.sample_rate,
        )

    # ======================================================
    # Pitch Extraction
    # ======================================================

    def extract_pitch_track(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:

        try:

            f0, _, _ = librosa.pyin(
                audio,
                fmin=FMIN_HZ,
                fmax=FMAX_HZ,
                sr=sample_rate,
                frame_length=2048,
                hop_length=256,
            )

        except Exception as exc:

            raise ValueError(
                "Unable to extract fundamental frequency."
            ) from exc

        if f0 is None:

            raise ValueError(
                "Pitch extraction returned no data."
            )

        valid_f0 = f0[
            np.isfinite(f0)
        ]

        valid_f0 = valid_f0[
            valid_f0 >= FMIN_HZ
        ]

        valid_f0 = valid_f0[
            valid_f0 <= FMAX_HZ
        ]

        if len(valid_f0) < 10:

            raise ValueError(
                "Not enough voiced samples detected "
                "for pitch analysis."
            )

        return valid_f0.astype(
            np.float64
        )

    # ======================================================
    # Pitch Features
    # ======================================================

    def extract_pitch_from_track(
        self,
        pitch: np.ndarray,
    ) -> Dict[str, float]:

        values = {

            "MDVP:Fo(Hz)": float(
                np.mean(pitch)
            ),

            "MDVP:Fhi(Hz)": float(
                np.max(pitch)
            ),

            "MDVP:Flo(Hz)": float(
                np.min(pitch)
            ),
        }

        self._validate_values(
            values
        )

        return values

    # ======================================================
    # Jitter
    # ======================================================

    def extract_jitter_from_track(
        self,
        pitch: np.ndarray,
    ) -> Dict[str, float]:

        periods = (
            1.0
            / pitch
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

        # --------------------------------------------------
        # Jitter absolute
        # --------------------------------------------------

        differences = np.abs(
            np.diff(periods)
        )

        jitter_abs = float(
            np.mean(
                differences
            )
        )

        # --------------------------------------------------
        # Jitter percentage
        # --------------------------------------------------

        jitter_percent = (
            jitter_abs
            / mean_period
        )

        # --------------------------------------------------
        # RAP
        # --------------------------------------------------

        rap_values = []

        for i in range(
            1,
            len(periods) - 1,
        ):

            local_average = (
                periods[i - 1]
                + periods[i]
                + periods[i + 1]
            ) / 3.0

            rap_values.append(
                abs(
                    periods[i]
                    - local_average
                )
            )

        if rap_values:

            rap = float(
                np.mean(
                    rap_values
                )
                / mean_period
            )

        else:

            rap = 0.0

        # --------------------------------------------------
        # PPQ
        # --------------------------------------------------

        ppq_values = []

        if len(periods) >= 5:

            for i in range(
                2,
                len(periods) - 2,
            ):

                local_average = float(
                    np.mean(
                        periods[
                            i - 2:
                            i + 3
                        ]
                    )
                )

                ppq_values.append(
                    abs(
                        periods[i]
                        - local_average
                    )
                )

        if ppq_values:

            ppq = float(
                np.mean(
                    ppq_values
                )
                / mean_period
            )

        else:

            ppq = rap

        # --------------------------------------------------
        # DDP
        # --------------------------------------------------

        ddp = float(
            rap * 3.0
        )

        values = {

            "MDVP:Jitter(%)":
                float(jitter_percent),

            "MDVP:Jitter(Abs)":
                float(jitter_abs),

            "MDVP:RAP":
                float(rap),

            "MDVP:PPQ":
                float(ppq),

            "Jitter:DDP":
                float(ddp),
        }

        self._validate_values(
            values
        )

        return values

    # ======================================================
    # RMS
    # ======================================================

    def extract_rms_track(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:

        rms = librosa.feature.rms(
            y=audio,
            frame_length=2048,
            hop_length=256,
        )[0]

        rms = rms[
            np.isfinite(rms)
        ]

        rms = rms[
            rms > 1e-10
        ]

        if len(rms) < 15:

            raise ValueError(
                "Not enough amplitude frames "
                "for shimmer analysis."
            )

        return rms.astype(
            np.float64
        )

    # ======================================================
    # Shimmer
    # ======================================================

    def extract_shimmer_from_rms(
        self,
        rms: np.ndarray,
    ) -> Dict[str, float]:

        mean_amplitude = float(
            np.mean(rms)
        )

        if mean_amplitude <= 0:

            raise ValueError(
                "Invalid mean amplitude."
            )

        # --------------------------------------------------
        # Shimmer
        # --------------------------------------------------

        amplitude_differences = np.abs(
            np.diff(rms)
        )

        shimmer = float(
            np.mean(
                amplitude_differences
            )
            / mean_amplitude
        )

        # --------------------------------------------------
        # Shimmer dB
        # --------------------------------------------------

        ratios = (
            rms[1:]
            / np.maximum(
                rms[:-1],
                1e-12,
            )
        )

        ratios = ratios[
            np.isfinite(ratios)
            & (ratios > 0)
        ]

        if len(ratios) > 0:

            shimmer_db = float(
                np.mean(
                    np.abs(
                        20.0
                        * np.log10(
                            ratios
                        )
                    )
                )
            )

        else:

            shimmer_db = 0.0

        # --------------------------------------------------
        # APQ
        # --------------------------------------------------

        def calculate_apq(
            window: int,
        ) -> float:

            if len(rms) < window:

                return shimmer

            half = window // 2

            values = []

            for i in range(
                half,
                len(rms) - half,
            ):

                local = rms[
                    i - half:
                    i + half + 1
                ]

                average = float(
                    np.mean(local)
                )

                if average <= 0:

                    continue

                values.append(
                    abs(
                        rms[i]
                        - average
                    )
                    / average
                )

            if not values:

                return shimmer

            return float(
                np.mean(values)
            )

        apq3 = calculate_apq(
            3
        )

        apq5 = calculate_apq(
            5
        )

        apq = calculate_apq(
            11
        )

        dda = float(
            apq3 * 3.0
        )

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

        self._validate_values(
            values
        )

        return values

    # ======================================================
    # HNR / NHR
    # ======================================================

    def extract_hnr_nhr(
        self,
        audio: np.ndarray,
        pitch: np.ndarray,
    ) -> Dict[str, float]:

        harmonic, _ = (
            librosa.effects.hpss(
                audio
            )
        )

        harmonic_energy = float(
            np.mean(
                harmonic ** 2
            )
        )

        total_energy = float(
            np.mean(
                audio ** 2
            )
        )

        harmonic_energy = max(
            harmonic_energy,
            1e-12,
        )

        total_energy = max(
            total_energy,
            harmonic_energy,
        )

        noise_energy = max(
            total_energy
            - harmonic_energy,
            1e-12,
        )

        hnr = float(
            10.0
            * np.log10(
                harmonic_energy
                / noise_energy
            )
        )

        nhr = float(
            noise_energy
            / harmonic_energy
        )

        values = {

            "NHR":
                nhr,

            "HNR":
                hnr,
        }

        self._validate_values(
            values
        )

        return values

    # ======================================================
    # RPDE
    # ======================================================

    def calculate_rpde(
        self,
        signal: np.ndarray,
    ) -> float:

        signal = np.asarray(
            signal,
            dtype=np.float64,
        )

        if len(signal) > MAX_NONLINEAR_SAMPLES:

            indices = np.linspace(
                0,
                len(signal) - 1,
                MAX_NONLINEAR_SAMPLES,
                dtype=np.int32,
            )

            signal = signal[
                indices
            ]

        signal = (
            signal
            - np.mean(signal)
        )

        std = float(
            np.std(signal)
        )

        if std <= 1e-12:

            return 0.0

        signal = (
            signal
            / std
        )

        n = len(signal)

        size = 1

        while size < (
            2 * n
        ):

            size *= 2

        spectrum = np.fft.rfft(
            signal,
            size,
        )

        autocorrelation = (
            np.fft.irfft(
                spectrum
                * np.conjugate(
                    spectrum
                ),
                size,
            )
            [:n]
        )

        if (
            len(autocorrelation) == 0
            or autocorrelation[0] <= 0
        ):

            return 0.0

        autocorrelation = (
            autocorrelation
            / autocorrelation[0]
        )

        autocorrelation = np.abs(
            autocorrelation[1:]
        )

        autocorrelation = autocorrelation[
            np.isfinite(
                autocorrelation
            )
        ]

        autocorrelation = np.clip(
            autocorrelation,
            0.0,
            1.0,
        )

        if len(autocorrelation) == 0:

            return 0.0

        histogram, _ = np.histogram(
            autocorrelation,
            bins=40,
            range=(0.0, 1.0),
        )

        histogram = histogram.astype(
            np.float64
        )

        total = float(
            np.sum(histogram)
        )

        if total <= 0:

            return 0.0

        probability = (
            histogram
            / total
        )

        probability = probability[
            probability > 0
        ]

        entropy = float(
            -np.sum(
                probability
                * np.log2(
                    probability
                )
            )
        )

        maximum_entropy = np.log2(
            40.0
        )

        if maximum_entropy <= 0:

            return 0.0

        return float(
            entropy
            / maximum_entropy
        )

    # ======================================================
    # DFA
    # ======================================================

    def calculate_dfa(
        self,
        signal: np.ndarray,
    ) -> float:

        signal = np.asarray(
            signal,
            dtype=np.float64,
        )

        if len(signal) > MAX_NONLINEAR_SAMPLES:

            indices = np.linspace(
                0,
                len(signal) - 1,
                MAX_NONLINEAR_SAMPLES,
                dtype=np.int32,
            )

            signal = signal[
                indices
            ]

        signal = (
            signal
            - np.mean(signal)
        )

        profile = np.cumsum(
            signal
        )

        n = len(profile)

        if n < 128:

            return 0.5

        min_window = 16

        max_window = min(
            n // 4,
            1024,
        )

        if max_window <= min_window:

            return 0.5

        windows = np.unique(
            np.logspace(
                np.log10(
                    min_window
                ),
                np.log10(
                    max_window
                ),
                num=10,
            ).astype(
                int
            )
        )

        log_windows = []

        log_fluctuations = []

        for window in windows:

            segments = (
                n
                // window
            )

            if segments < 2:

                continue

            fluctuations = []

            x = np.arange(
                window,
                dtype=np.float64,
            )

            for segment_index in range(
                segments
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

                if len(segment) != window:

                    continue

                try:

                    coefficients = (
                        np.polyfit(
                            x,
                            segment,
                            1,
                        )
                    )

                    trend = (
                        np.polyval(
                            coefficients,
                            x,
                        )
                    )

                    residual = (
                        segment
                        - trend
                    )

                    fluctuation = float(
                        np.sqrt(
                            np.mean(
                                residual ** 2
                            )
                        )
                    )

                except Exception:

                    continue

                if (
                    np.isfinite(
                        fluctuation
                    )
                    and fluctuation > 0
                ):

                    fluctuations.append(
                        fluctuation
                    )

            if not fluctuations:

                continue

            fluctuation_mean = float(
                np.mean(
                    fluctuations
                )
            )

            if fluctuation_mean <= 0:

                continue

            log_windows.append(
                np.log(
                    float(window)
                )
            )

            log_fluctuations.append(
                np.log(
                    fluctuation_mean
                )
            )

        if len(log_windows) < 3:

            return 0.5

        try:

            slope = np.polyfit(
                np.asarray(
                    log_windows
                ),
                np.asarray(
                    log_fluctuations
                ),
                1,
            )[0]

        except Exception:

            return 0.5

        if not np.isfinite(
            slope
        ):

            return 0.5

        return float(
            np.clip(
                slope,
                0.0,
                2.0,
            )
        )

    # ======================================================
    # Spread Features
    # ======================================================

    def calculate_spread_features(
        self,
        pitch: np.ndarray,
    ) -> Tuple[float, float]:

        log_pitch = np.log(
            np.maximum(
                pitch,
                1e-12,
            )
        )

        spread1 = float(
            np.std(
                log_pitch
            )
        )

        if len(log_pitch) > 1:

            spread2 = float(
                np.std(
                    np.diff(
                        log_pitch
                    )
                )
            )

        else:

            spread2 = 0.0

        return (
            spread1,
            spread2,
        )

    # ======================================================
    # D2
    # ======================================================

    def calculate_d2(
        self,
        pitch: np.ndarray,
    ) -> float:

        x = np.asarray(
            pitch,
            dtype=np.float64,
        )

        if len(x) > 1000:

            indices = np.linspace(
                0,
                len(x) - 1,
                1000,
                dtype=np.int32,
            )

            x = x[
                indices
            ]

        if len(x) < 100:

            return 0.0

        x = (
            x
            - np.mean(x)
        )

        std = float(
            np.std(x)
        )

        if std <= 1e-12:

            return 0.0

        x = (
            x
            / std
        )

        dimension = 2

        delay = 1

        count = (
            len(x)
            - (
                dimension
                - 1
            )
            * delay
        )

        if count < 50:

            return 0.0

        embedded = np.empty(
            (
                count,
                dimension,
            ),
            dtype=np.float64,
        )

        embedded[:, 0] = x[
            :count
        ]

        embedded[:, 1] = x[
            delay:
            delay + count
        ]

        max_points = min(
            len(embedded),
            400,
        )

        if len(embedded) > max_points:

            indices = np.linspace(
                0,
                len(embedded) - 1,
                max_points,
                dtype=np.int32,
            )

            embedded = embedded[
                indices
            ]

        differences = (
            embedded[:, None, :]
            - embedded[None, :, :]
        )

        distances = np.sqrt(
            np.sum(
                differences ** 2,
                axis=2,
            )
        )

        upper = distances[
            np.triu_indices(
                len(embedded),
                k=1,
            )
        ]

        upper = upper[
            np.isfinite(
                upper
            )
            & (
                upper > 0
            )
        ]

        if len(upper) < 20:

            return 0.0

        radii = np.percentile(
            upper,
            [
                10,
                20,
                30,
                40,
            ],
        )

        log_r = []

        log_c = []

        total_pairs = float(
            len(upper)
        )

        for radius in radii:

            if radius <= 0:

                continue

            count_pairs = float(
                np.sum(
                    upper < radius
                )
            )

            if count_pairs <= 0:

                continue

            correlation_sum = (
                count_pairs
                / total_pairs
            )

            if correlation_sum <= 0:

                continue

            log_r.append(
                np.log(
                    radius
                )
            )

            log_c.append(
                np.log(
                    correlation_sum
                )
            )

        if len(log_r) < 2:

            return 0.0

        try:

            slope = np.polyfit(
                np.asarray(
                    log_r
                ),
                np.asarray(
                    log_c
                ),
                1,
            )[0]

            d2 = abs(
                float(slope)
            )

        except Exception:

            return 0.0

        if not np.isfinite(
            d2
        ):

            return 0.0

        return float(
            np.clip(
                d2,
                0.0,
                10.0,
            )
        )

    # ======================================================
    # PPE
    # ======================================================

    def calculate_ppe(
        self,
        pitch: np.ndarray,
    ) -> float:

        log_pitch = np.log(
            np.maximum(
                pitch,
                1e-12,
            )
        )

        mean = float(
            np.mean(
                log_pitch
            )
        )

        std = float(
            np.std(
                log_pitch
            )
        )

        if std <= 1e-12:

            return 0.0

        z = (
            log_pitch
            - mean
        ) / std

        histogram, _ = np.histogram(
            z,
            bins=32,
            range=(
                -4.0,
                4.0,
            ),
        )

        histogram = histogram.astype(
            np.float64
        )

        total = float(
            np.sum(
                histogram
            )
        )

        if total <= 0:

            return 0.0

        probability = (
            histogram
            / total
        )

        probability = probability[
            probability > 0
        ]

        entropy = float(
            -np.sum(
                probability
                * np.log(
                    probability
                )
            )
        )

        return float(
            entropy
            / np.log(
                32.0
            )
        )

    # ======================================================
    # Nonlinear Features
    # ======================================================

    def extract_nonlinear_features(
        self,
        audio: np.ndarray,
        sample_rate: int,
        pitch: np.ndarray,
    ) -> Dict[str, float]:

        signal = np.asarray(
            audio,
            dtype=np.float64,
        )

        if len(signal) > MAX_NONLINEAR_SAMPLES:

            indices = np.linspace(
                0,
                len(signal) - 1,
                MAX_NONLINEAR_SAMPLES,
                dtype=np.int32,
            )

            signal = signal[
                indices
            ]

        signal = (
            signal
            - np.mean(signal)
        )

        std = float(
            np.std(signal)
        )

        if std > 1e-12:

            signal = (
                signal
                / std
            )

        else:

            signal = np.zeros_like(
                signal
            )

        rpde = self.calculate_rpde(
            signal
        )

        dfa = self.calculate_dfa(
            signal
        )

        spread1, spread2 = (
            self.calculate_spread_features(
                pitch
            )
        )

        d2 = self.calculate_d2(
            pitch
        )

        ppe = self.calculate_ppe(
            pitch
        )

        values = {

            "RPDE":
                float(rpde),

            "DFA":
                float(dfa),

            "spread1":
                float(spread1),

            "spread2":
                float(spread2),

            "D2":
                float(d2),

            "PPE":
                float(ppe),
        }

        self._validate_values(
            values
        )

        return values

    # ======================================================
    # Extract All 22 Features
    # ======================================================

    def extract_features(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> Dict[str, float]:
        """
        Extract exactly 22 features.

        Pitch detection is performed once and reused.
        """

        # --------------------------------------------------
        # Preprocess
        # --------------------------------------------------

        (
            processed_audio,
            processed_rate,
        ) = self.preprocess_audio(
            audio,
            sample_rate,
        )

        # --------------------------------------------------
        # ONE pitch extraction
        # --------------------------------------------------

        pitch = self.extract_pitch_track(
            processed_audio,
            processed_rate,
        )

        # --------------------------------------------------
        # Pitch features
        # --------------------------------------------------

        pitch_features = (
            self.extract_pitch_from_track(
                pitch
            )
        )

        # --------------------------------------------------
        # Jitter
        # --------------------------------------------------

        jitter_features = (
            self.extract_jitter_from_track(
                pitch
            )
        )

        # --------------------------------------------------
        # RMS / Shimmer
        # --------------------------------------------------

        rms = self.extract_rms_track(
            processed_audio
        )

        shimmer_features = (
            self.extract_shimmer_from_rms(
                rms
            )
        )

        # --------------------------------------------------
        # HNR / NHR
        # --------------------------------------------------

        hnr_features = (
            self.extract_hnr_nhr(
                processed_audio,
                pitch,
            )
        )

        # --------------------------------------------------
        # Nonlinear features
        # --------------------------------------------------

        nonlinear_features = (
            self.extract_nonlinear_features(
                processed_audio,
                processed_rate,
                pitch,
            )
        )

        # --------------------------------------------------
        # Assemble in exact order
        # --------------------------------------------------

        features = {

            "MDVP:Fo(Hz)":
                pitch_features[
                    "MDVP:Fo(Hz)"
                ],

            "MDVP:Fhi(Hz)":
                pitch_features[
                    "MDVP:Fhi(Hz)"
                ],

            "MDVP:Flo(Hz)":
                pitch_features[
                    "MDVP:Flo(Hz)"
                ],

            "MDVP:Jitter(%)":
                jitter_features[
                    "MDVP:Jitter(%)"
                ],

            "MDVP:Jitter(Abs)":
                jitter_features[
                    "MDVP:Jitter(Abs)"
                ],

            "MDVP:RAP":
                jitter_features[
                    "MDVP:RAP"
                ],

            "MDVP:PPQ":
                jitter_features[
                    "MDVP:PPQ"
                ],

            "Jitter:DDP":
                jitter_features[
                    "Jitter:DDP"
                ],

            "MDVP:Shimmer":
                shimmer_features[
                    "MDVP:Shimmer"
                ],

            "MDVP:Shimmer(dB)":
                shimmer_features[
                    "MDVP:Shimmer(dB)"
                ],

            "Shimmer:APQ3":
                shimmer_features[
                    "Shimmer:APQ3"
                ],

            "Shimmer:APQ5":
                shimmer_features[
                    "Shimmer:APQ5"
                ],

            "MDVP:APQ":
                shimmer_features[
                    "MDVP:APQ"
                ],

            "Shimmer:DDA":
                shimmer_features[
                    "Shimmer:DDA"
                ],

            "NHR":
                hnr_features[
                    "NHR"
                ],

            "HNR":
                hnr_features[
                    "HNR"
                ],

            "RPDE":
                nonlinear_features[
                    "RPDE"
                ],

            "DFA":
                nonlinear_features[
                    "DFA"
                ],

            "spread1":
                nonlinear_features[
                    "spread1"
                ],

            "spread2":
                nonlinear_features[
                    "spread2"
                ],

            "D2":
                nonlinear_features[
                    "D2"
                ],

            "PPE":
                nonlinear_features[
                    "PPE"
                ],
        }

        # --------------------------------------------------
        # Final validation
        # --------------------------------------------------

        self.validate_feature_dictionary(
            features
        )

        return features

    # ======================================================
    # Extract From File
    # ======================================================

    def extract_features_from_file(
        self,
        audio_path: str,
    ) -> Dict[str, float]:

        audio, sample_rate = (
            self.load_audio(
                audio_path
            )
        )

        return self.extract_features(
            audio,
            sample_rate,
        )

    # ======================================================
    # Feature Vector
    # ======================================================

    def feature_vector(
        self,
        features: Dict[str, float],
    ) -> List[float]:
        """
        Return the 22 values in the exact
        model feature order.
        """

        self.validate_feature_dictionary(
            features
        )

        return [
            float(
                features[name]
            )
            for name in FEATURE_NAMES
        ]

    # ======================================================
    # Backward Compatibility
    # ======================================================

    def to_feature_vector(
        self,
        features: Dict[str, float],
    ) -> List[float]:
        """
        Backward-compatible alias.

        prediction_service.py currently expects:

            audio_feature_service.to_feature_vector()

        Keep this method so the existing prediction
        service does not fail.
        """

        return self.feature_vector(
            features
        )

    # ======================================================
    # Validate Feature Dictionary
    # ======================================================

    def validate_feature_dictionary(
        self,
        features: Dict[str, float],
    ) -> bool:

        if not isinstance(
            features,
            dict,
        ):

            raise ValueError(
                "Features must be a dictionary."
            )

        missing = [
            name
            for name in FEATURE_NAMES
            if name not in features
        ]

        if missing:

            raise ValueError(
                "Missing required features: "
                + ", ".join(
                    missing
                )
            )

        if len(features) != TOTAL_FEATURES:

            raise ValueError(
                "Exactly 22 features are required. "
                f"Found {len(features)}."
            )

        ordered_values = {
            name: features[name]
            for name in FEATURE_NAMES
        }

        self._validate_values(
            ordered_values
        )

        return True

    # ======================================================
    # Numeric Validation
    # ======================================================

    @staticmethod
    def _validate_values(
        values: Dict[str, float],
    ) -> None:

        for name, value in values.items():

            try:

                numeric_value = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    f"Feature {name} "
                    "must be numeric."
                )

            if not np.isfinite(
                numeric_value
            ):

                raise ValueError(
                    f"Feature {name} "
                    "contains an invalid value."
                )

    # ======================================================
    # Audio Information
    # ======================================================

    def audio_information(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> Dict:

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

            "sample_rate":
                int(sample_rate),

            "samples":
                int(len(audio)),

            "duration":
                float(duration),

            "channels":
                1,

            "peak":
                peak,

            "rms":
                rms,
        }


# ==========================================================
# Default Service Instance
# ==========================================================

audio_feature_service = (
    AudioFeatureService()
)
