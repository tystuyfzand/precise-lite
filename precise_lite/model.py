# Copyright 2019 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import attr
from os.path import isfile
from typing import *

from precise_lite.functions import load_keras, false_pos, false_neg, \
    weighted_log_loss, set_loss_bias
from precise_lite.params import inject_params, pr

if TYPE_CHECKING:
    from tensorflow.keras.models import Sequential


@attr.s()
class ModelParams:
    """
    Attributes:
        recurrent_units:
        dropout:
        extra_metrics: Whether to include false positive and false negative metrics
        skip_acc: Whether to skip accuracy calculation while training
    """
    recurrent_units = attr.ib(20)  # type: int
    dropout = attr.ib(0.2)  # type: float
    extra_metrics = attr.ib(False)  # type: bool
    skip_acc = attr.ib(False)  # type: bool
    loss_bias = attr.ib(0.7)  # type: float
    freeze_till = attr.ib(0)  # type: bool


def load_precise_model(model_name: str) -> Any:
    """Loads a Keras model from file, handling custom loss function"""
    if not model_name.endswith('.net'):
        print('Warning: Unknown model type, ', model_name)

    inject_params(model_name)
    from tensorflow.keras.models import load_model
    return load_model(model_name, custom_objects=globals())


def create_model(model_name: Optional[str], params: ModelParams) -> 'Sequential':
    """
    Load or create a precise_lite model

    Args:
        model_name: Name of model
        params: Parameters used to create the model

    Returns:
        model: Loaded Keras model
    """
    if model_name and isfile(model_name):
        print('Loading from ' + model_name + '...')
        model = load_precise_model(model_name)
    else:
        from tensorflow.keras.layers import Dense, GRU
        from tensorflow.keras.models import Sequential

        model = Sequential()
        model.add(GRU(
            params.recurrent_units, activation='linear',
            input_shape=(pr.n_features, pr.feature_size), dropout=params.dropout, name='net'
        ))
        model.add(Dense(1, activation='sigmoid'))

    metrics = ['accuracy'] + params.extra_metrics * [false_pos, false_neg]
    set_loss_bias(params.loss_bias)
    for i in model.layers[:params.freeze_till]:
        i.trainable = False
    model.compile('rmsprop', weighted_log_loss, metrics=(not params.skip_acc) * metrics)
    return model
