"""
Transfer function representation and analysis for control systems.
"""

from typing import Union, List, Optional, Tuple, TYPE_CHECKING
import numpy as np
from dataclasses import dataclass
from scipy import signal
from scipy.optimize import curve_fit

if TYPE_CHECKING:
    from .stability import StabilityMetrics


class TransferFunction:
    """
    Represents a linear transfer function H(s) = N(s)/D(s).

    Attributes:
        numerator_coeffs: Polynomial coefficients of numerator (highest degree first)
        denominator_coeffs: Polynomial coefficients of denominator (highest degree first)
    """

    def __init__(
        self, numerator: Union[List[float], np.ndarray], denominator: Union[List[float], np.ndarray]
    ):
        """
        Initialize transfer function from polynomial coefficients.

        Args:
            numerator: Coefficients of numerator polynomial [a_n, ..., a_1, a_0]
            denominator: Coefficients of denominator polynomial [b_m, ..., b_1, b_0]
        """
        # Convert to numpy arrays
        num = np.asarray(numerator, dtype=float)
        den = np.asarray(denominator, dtype=float)

        # Validate inputs
        if num.size == 0:
            raise ValueError("Numerator coefficients must be non-empty")
        if den.size == 0:
            raise ValueError("Denominator coefficients must be non-empty")

        # Remove leading zeros
        num = np.trim_zeros(num, "f")
        den = np.trim_zeros(den, "f")

        # Ensure arrays are not empty after trimming
        if num.size == 0:
            num = np.array([0.0])
        if den.size == 0:
            raise ValueError("Denominator leading coefficient must be non-zero")

        # Normalize by leading denominator coefficient
        if den[0] != 0:
            num = num / den[0]
            den = den / den[0]
        else:
            raise ValueError("Denominator leading coefficient must be non-zero")

        self.numerator_coeffs = num
        self.denominator_coeffs = den

    @classmethod
    def from_poles_zeros(
        cls,
        poles: Union[List[complex], np.ndarray],
        zeros: Union[List[complex], np.ndarray, None] = None,
        gain: float = 1.0,
    ) -> "TransferFunction":
        """
        Create transfer function from poles, zeros, and gain.

        Args:
            poles: List of pole locations (complex or real)
            zeros: List of zero locations (complex or real), or None/empty for no zeros
            gain: Overall system gain

        Returns:
            TransferFunction object
        """
        poles = np.asarray(poles)
        if zeros is None or len(zeros) == 0:
            zeros = np.array([])
        else:
            zeros = np.asarray(zeros)

        # Create polynomials from roots
        if len(zeros) > 0:
            num_poly = np.poly(zeros) * gain
        else:
            num_poly = np.array([gain])

        den_poly = np.poly(poles)

        return cls(num_poly, den_poly)

    @classmethod
    def from_frequency_response(
        cls,
        frequencies: np.ndarray,
        response: np.ndarray,
        order: Optional[int] = None,
        num_order: Optional[int] = None,
    ) -> "TransferFunction":
        """
        Fit transfer function to frequency response data.

        Args:
            frequencies: Angular frequencies in rad/s
            response: Complex frequency response H(jω)
            order: Order of denominator (auto-detect if None)
            num_order: Order of numerator (defaults to order-1 if None)

        Returns:
            Fitted TransferFunction object
        """
        frequencies = np.asarray(frequencies)
        response = np.asarray(response)
        
        # Check for valid input data
        if np.any(np.isnan(response)) or np.any(np.isinf(response)):
            raise ValueError("Invalid frequency response data: contains NaN or infinite values")
        
        if len(frequencies) != len(response):
            raise ValueError("Frequency and response arrays must have the same length")

        if order is None:
            # Auto-detect order based on phase change
            phase = np.unwrap(np.angle(response))
            phase_change = abs(phase[-1] - phase[0])
            
            # Handle edge cases where phase_change might be invalid
            if np.isnan(phase_change) or np.isinf(phase_change):
                order = 1  # Default to first order
            else:
                order = max(1, int(np.round(phase_change / (np.pi / 2))))

        if num_order is None:
            num_order = max(0, order - 1)

        # Use scipy.optimize.curve_fit for rational function fitting
        s = 1j * frequencies

        # For simple first-order, use analytical solution
        if order == 1 and num_order == 0:
            # H(s) = k/(s + a)
            # Find DC gain and pole location
            dc_gain = np.abs(response[0])

            # Find -3dB point for pole estimation
            target_mag = dc_gain / np.sqrt(2)
            idx = np.argmin(np.abs(np.abs(response) - target_mag))
            pole_freq = frequencies[idx]

            return cls([dc_gain * pole_freq], [1, pole_freq])

        # Use scipy.optimize.curve_fit for rational function fitting
        # This is the standard, proven approach for transfer function identification
        try:
            # Define rational function model for fitting
            def rational_function(w, *params):
                """Rational function H(jw) = P(jw)/Q(jw) for fitting."""
                w = np.atleast_1d(w)
                s = 1j * w
                
                # Split parameters into numerator and denominator coefficients
                n_num = num_order + 1
                num_coeffs = params[:n_num]
                den_coeffs = params[n_num:]
                
                # Evaluate polynomials
                numerator = np.polyval(num_coeffs, s)
                denominator = np.polyval([1] + list(den_coeffs), s)  # Leading coeff = 1
                
                return numerator / denominator
            
            # Prepare data for fitting
            magnitude = np.abs(response)
            phase = np.angle(response)
            
            # Use magnitude fitting for stable results
            def magnitude_model(w, *params):
                return np.abs(rational_function(w, *params))
            
            # Initial parameter guess
            # Start with simple estimates based on response characteristics
            dc_gain = magnitude[0] if len(magnitude) > 0 else 1.0
            
            # Initial guess: DC gain in numerator, simple poles in denominator  
            num_guess = [dc_gain] + [0] * num_order
            den_guess = [1] * order  # Will be combined with leading 1
            initial_guess = num_guess + den_guess
            
            # Fit the magnitude response
            try:
                popt, _ = curve_fit(
                    magnitude_model, 
                    frequencies, 
                    magnitude,
                    p0=initial_guess,
                    maxfev=5000,
                    method='lm'
                )
                
                # Extract fitted coefficients
                n_num = num_order + 1
                fitted_num = popt[:n_num]
                fitted_den = np.concatenate([[1], popt[n_num:]])
                
                return cls(fitted_num, fitted_den)
                
            except (RuntimeError, ValueError):
                # If fitting fails, fall back to simple approach
                pass
            
            # Fallback: Simple characteristic-based fitting
            if np.any(np.abs(response) > 1e-10):
                # Find peak response for resonant systems
                peak_idx = np.argmax(magnitude)
                peak_freq = frequencies[peak_idx]
                peak_gain = magnitude[peak_idx]
                dc_gain = magnitude[0]
                
                if peak_gain > dc_gain * 1.1:  # Resonant system
                    # Create second-order bandpass-like system
                    wn = peak_freq  # Approximate natural frequency
                    Q = peak_gain / dc_gain  # Rough Q estimate
                    
                    if order >= 2:
                        # Second-order system: H(s) = K*s / (s² + (wn/Q)*s + wn²)
                        return cls([peak_gain * wn], [1, wn/Q, wn**2])
                    else:
                        # First-order approximation
                        return cls([dc_gain * wn], [1, wn])
                else:
                    # Low-pass like system
                    # Find -3dB point
                    target_mag = dc_gain / np.sqrt(2)
                    idx = np.argmin(np.abs(magnitude - target_mag))
                    cutoff_freq = frequencies[idx] if idx < len(frequencies) else peak_freq
                    
                    return cls([dc_gain * cutoff_freq], [1, cutoff_freq])
            else:
                # Zero response
                return cls([0], [1])
                
        except Exception:
            # Ultimate fallback
            return cls([1], [1])

    @property
    def order(self) -> int:
        """Order of the transfer function (degree of denominator)."""
        return len(self.denominator_coeffs) - 1

    @property
    def poles(self) -> np.ndarray:
        """Poles of the transfer function (roots of denominator)."""
        if len(self.denominator_coeffs) == 1:
            # Constant denominator, no poles
            return np.array([])
        return np.roots(self.denominator_coeffs)

    @property
    def zeros(self) -> np.ndarray:
        """Zeros of the transfer function (roots of numerator)."""
        if len(self.numerator_coeffs) == 1:
            # Constant numerator
            if self.numerator_coeffs[0] == 0:
                # Zero numerator means undefined zeros
                return np.array([])
            else:
                # Non-zero constant has no zeros
                return np.array([])
        return np.roots(self.numerator_coeffs)

    @property
    def dc_gain(self) -> float:
        """DC gain of the transfer function H(0)."""
        result = self.evaluate(0)
        if isinstance(result, np.ndarray):
            return float(result.real)
        return float(result.real)

    @property
    def bandwidth(self) -> float:
        """
        3dB bandwidth in rad/s.

        Returns:
            Angular frequency where |H(jω)| = |H(0)|/√2
        """
        # Calculate magnitude at DC
        dc_mag = abs(self.evaluate(0))
        target_mag = dc_mag / np.sqrt(2)

        # Search for -3dB point
        # Use a logarithmic search from 0.001 to 10000 rad/s
        frequencies = np.logspace(-3, 4, 1000)
        response = self.frequency_response(frequencies)
        magnitudes = np.abs(response)

        # Find closest point to -3dB
        idx = np.argmin(np.abs(magnitudes - target_mag))

        # Refine with interpolation if needed
        if idx > 0 and idx < len(frequencies) - 1:
            # Linear interpolation in log space
            f_low = frequencies[idx - 1]
            f_high = frequencies[idx + 1]
            m_low = magnitudes[idx - 1]
            m_high = magnitudes[idx + 1]

            # Interpolate to find exact crossing
            if m_low != m_high:
                alpha = (target_mag - m_low) / (m_high - m_low)
                bandwidth = f_low * (f_high / f_low) ** alpha
            else:
                bandwidth = frequencies[idx]
        else:
            bandwidth = frequencies[idx]

        return float(bandwidth)

    @property
    def is_stable(self) -> bool:
        """
        Check if system is stable (all poles in left half-plane).

        Returns:
            True if all poles have negative real parts
        """
        poles = self.poles
        if len(poles) == 0:
            return True
        return bool(np.all(np.real(poles) < 0))

    def evaluate(self, s: Union[complex, float, np.ndarray]) -> Union[complex, np.ndarray]:
        """
        Evaluate transfer function at given s values.

        Args:
            s: Complex frequency value(s) to evaluate at

        Returns:
            H(s) evaluated at the given point(s)
        """
        s = np.asarray(s)
        scalar_input = s.ndim == 0
        s = np.atleast_1d(s)

        # Evaluate polynomials
        num_val = np.polyval(self.numerator_coeffs, s)
        den_val = np.polyval(self.denominator_coeffs, s)

        # Compute H(s) = N(s)/D(s)
        with np.errstate(divide="ignore", invalid="ignore"):
            result = num_val / den_val

        if scalar_input:
            return complex(result[0])
        return result

    def frequency_response(self, frequencies: np.ndarray) -> np.ndarray:
        """
        Compute frequency response H(jω) at given frequencies.

        Args:
            frequencies: Angular frequencies in rad/s

        Returns:
            Complex frequency response H(jω)
        """
        s = 1j * np.asarray(frequencies)
        result = self.evaluate(s)
        if isinstance(result, np.ndarray):
            return result
        return np.array([result])

    def __str__(self) -> str:
        """String representation of transfer function."""
        return (
            f"Transfer Function H(s)\n"
            f"  Order: {self.order}\n"
            f"  Poles: {len(self.poles)}\n"
            f"  Zeros: {len(self.zeros)}\n"
            f"  DC Gain: {self.dc_gain:.3f}"
        )

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"TransferFunction(numerator={self.numerator_coeffs.tolist()}, "
            f"denominator={self.denominator_coeffs.tolist()})"
        )

    def stability_margins(self) -> "StabilityMetrics":
        """
        Calculate stability margins (phase and gain).

        Returns:
            StabilityMetrics object with margins
        """
        from .stability import calculate_stability_margins

        return calculate_stability_margins(self)

    def step_response(self, time: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate unit step response.

        Args:
            time: Time vector (auto-generated if None)

        Returns:
            Tuple of (time, response) arrays
        """
        from .time_domain import step_response

        return step_response(self, time)

    def impulse_response(self, time: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate impulse response.

        Args:
            time: Time vector (auto-generated if None)

        Returns:
            Tuple of (time, response) arrays
        """
        from .time_domain import impulse_response

        return impulse_response(self, time)

    def rise_time(self) -> float:
        """Calculate 10-90% rise time of step response."""
        from .time_domain import calculate_rise_time

        t, y = self.step_response()
        return calculate_rise_time(t, y)

    def settling_time(self, tolerance: float = 0.02) -> float:
        """Calculate settling time to within tolerance."""
        from .time_domain import calculate_settling_time

        t, y = self.step_response()
        return calculate_settling_time(t, y, tolerance)

    def overshoot(self) -> float:
        """Calculate percent overshoot of step response."""
        from .time_domain import calculate_overshoot

        _, y = self.step_response()
        return calculate_overshoot(y)
