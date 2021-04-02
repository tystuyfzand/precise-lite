# Mycroft Precise

*A lightweight, simple-to-use, RNN wake word listener.*

Precise is a wake word listener.  The software monitors an audio stream ( usually a microphone ) and when it recognizes a specific phrase it triggers an event.  For example, at Mycroft AI the team has trained Precise to recognize the phrase "Hey, Mycroft".  When the software recognizes this phrase it puts the rest of Mycroft's software into command mode and waits for a command from the person using the device.  Mycroft Precise is fully open source and can be trined to recognize anything from a name to a cough.

In addition to Precise there are several proprietary wake word listeners out there.  If you are looking to spot a wakeword Precise might be a great solution, but if it's too resource intensive or isn't accurate enough here are some [alternative options][comparison].

[comparison]: https://github.com/MycroftAI/mycroft-precise/wiki/Software-Comparison

## Supported Operating Systems

Precise is designed to run on Linux.  It is known to work on a variety of Linux distributions including Debian, Ubuntu and Raspbian.  It probably operates on other \*nx distributions.

## Training Models

### Train your own model

You can find info on training your own models [here][train-guide]. It requires
running through the [**source install instructions**][source-install] first.

**Note: Please use the training-guide mentioned in the link. It's really helpful and the repo is tested using the commands mentioend in the link.**
[train-guide]:https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word#how-to-train-your-own-wake-word

## Installation

First create a virtual environment to install python packages.

```python3 -m venv venv-name
source /path/to/venv/venv-name/bin/activate
pip intsall --upgrade pip
```

### Source Install

Start out by cloning `dev` branch of the repository:

```bash
git clone https://github.com/bkhti4/mycroft-precise.git
cd mycroft-precise
```

After this, run the setup script:

```bash
./setup.sh
```

Finally, you can write your program and run it as follows:
```bash
source ./path/to/venv/venv-name/bin/activate  # Change the python environment to include precise library
```

Sample Python program:
```python
#!/usr/bin/env python3

from precise_runner import PreciseEngine, PreciseRunner

engine = PreciseEngine('.venv/bin/precise-engine', 'my_model_file.pb')
runner = PreciseRunner(engine, on_activation=lambda: print('hello'))
runner.start()
```

In addition to the `precise-engine` executable, doing a **Source Install** gives you
access to some other scripts. You can read more about them [here][executables].
One of these executables, `precise-listen`, can be used to test a model using
your microphone:

[executables]:https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word#how-to-train-your-own-wake-word

```bash
source .venv/bin/activate  # Gain access to precise-* executables
precise-listen my_model_file.pb
```
