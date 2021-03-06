import random as rd
import tensorflow as tf

BATCH_SIZE = -1
BETA1 = 0.5
BETA2 = 0.9
CHANNELS = 1
CLASSES = 2
KERNEL_SIZE = 25
LEARN_RATE = 0.0001
MODEL_SIZE = 16
PHASE_SHUFFLE = 2
STRIDE = 4
WAV_LENGTH = 1024


def network(features, labels, mode):
    """ A waveGAN discriminator """

    labels = tf.reshape(
        tensor=tf.cast(labels, tf.int32),
        shape=[BATCH_SIZE, 1],
        name='Labels'
    )

    inputLayer = tf.reshape(
        tensor=tf.cast(features['x'], tf.float32),
        shape=[BATCH_SIZE, WAV_LENGTH, CHANNELS],
        name='InputLayer'
    )

    # Input: [64, 1024, 1] > [64, 256, 16]
    convolution1 = tf.layers.conv1d(
        inputs=inputLayer,
        filters=MODEL_SIZE,
        kernel_size=KERNEL_SIZE,
        strides=STRIDE,
        padding='same',
        use_bias=True,
        activation=tf.nn.leaky_relu,
        name="Convolution1"
    )

    convolution1 = _phaseShuffle(convolution1)

    # Input: [64, 256, 16] > [64, 64, 32]
    convolution2 = tf.layers.conv1d(
        inputs=convolution1,
        filters=MODEL_SIZE * 2,
        kernel_size=KERNEL_SIZE,
        strides=STRIDE,
        padding='same',
        use_bias=True,
        activation=tf.nn.leaky_relu,
        name="Convolution2"
    )

    convolution2 = _phaseShuffle(convolution2)

    # Input: [64, 64, 32] > [64, 16, 64]
    convolution3 = tf.layers.conv1d(
        inputs=convolution2,
        filters=MODEL_SIZE * 4,
        kernel_size=KERNEL_SIZE,
        strides=STRIDE,
        padding='same',
        use_bias=True,
        activation=tf.nn.leaky_relu,
        name="Convolution3"
    )

    # Input: [64, 16, 64] > [64, 1024]
    flatten = tf.reshape(
        tensor=convolution3,
        shape=[BATCH_SIZE, WAV_LENGTH],
        name="Output"
    )

    # Input: [64, 1024] > [64, 1]
    logits = tf.layers.dense(
        inputs=flatten,
        units=CLASSES,
        name='Logits'
    )[:, :]

    loss = tf.reduce_mean(
        tf.losses.sparse_softmax_cross_entropy(
            logits=logits,
            labels=labels[:, :]
        )
    )

    optimizer = tf.train.AdamOptimizer(
        learning_rate=LEARN_RATE,
        beta1=BETA1,
        beta2=BETA2
    )

    train_op_param = optimizer.minimize(
        loss=loss,
        global_step=tf.train.get_global_step()
    )

    predictions = {
        'classes': tf.argmax(logits, axis=1),
        'probabilities': tf.nn.softmax(logits)
    }

    eval_metrics = {
        'accuracy': tf.metrics.accuracy(
            labels=labels,
            predictions=predictions['classes']
        )
    }

    estimator = tf.estimator.EstimatorSpec(
        eval_metric_ops=eval_metrics,
        loss=loss,
        train_op=train_op_param,
        mode=mode
    )

    return estimator


def _phaseShuffle(layer):
    """ Shuffles the phase of each layer """
    batch, length, channel = layer.get_shape().as_list()
    shuffle = _returnPhaseShuffleValue()
    lft = max(0, shuffle)
    rgt = max(0, -shuffle)
    layer = tf.pad(
        tensor=layer,
        paddings=[[0, 0], [lft, rgt], [0, 0]],
        mode='REFLECT'
    )
    layer = layer[:, rgt:rgt+length]
    layer.set_shape([batch, length, channel])
    return layer


def _returnPhaseShuffleValue():
    """ Returns a a ranom integer in the range decided for phase shuffle"""
    return rd.randint(-PHASE_SHUFFLE, PHASE_SHUFFLE)
