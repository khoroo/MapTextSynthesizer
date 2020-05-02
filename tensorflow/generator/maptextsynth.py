# CNN-LSTM-CTC-OCR
# Copyright (C) 2017,2018 Jerod Weinman, Abyaya Lamsal, Benjamin Gafford
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# maptextsynth.py -- Input pipeline for dynamically generated
#   synthetic text images

import os
import tensorflow as tf
import numpy as np
from data_synth import multithreaded_data_generator as data_generator
import pipeline
import charset

def get_dataset( args=None ):
    """
    Get a dataset from generator 
    Format: [text|image|labels] -- types and shapes can be seen below 
    """
    
    def _generator_wrapper():
        """
        Wraps data_generator to precompute labels in python before everything
        becomes tensors. 
        NOTE: Local to get_dataset for sensible passing of args to generator
        function.  
        Returns:
        caption : ground truth string
        image   : raw mat object image [32, ?, 1] 
        label   : list of indices corresponding to out_charset plus a temporary
                  increment; length=len( caption )
        """
    
        # Extract args
        [ config_path, num_producers ] = args[0:2]

        # TODO/NOTE currently using 0 to get true single threaded synthesis
        gen = data_generator( config_path, num_producers )

        while True:
            caption, image = next( gen )
            caption = str(caption)

            # Transform string text to sequence of indices using charset dict
            label = charset.string_to_label(caption)

            # Temporarily increment all labels so that zero can be the EOS token
            # during post-batch dense-to-sparse conversion
            label = [index+1 for index in label]

            yield caption, image, label

        
    return tf.data.Dataset.from_generator( 
        _generator_wrapper, 
        (tf.string, tf.uint8, tf.int32),   # Output Types
        (tf.TensorShape( [] ),             # Text shape
         tf.TensorShape( (32, None, 1) ),  # Image shape
         tf.TensorShape( [None] )) )       # Labels shape
    

def preprocess_fn( caption, image, labels ):
    """
    Reformat raw data for model trainer. 
    Intended to get data as formatted from get_dataset function.
    Parameters:
      caption : tf.string corresponding to text
      image   : tf.uint8 tensor of shape [32, ?, 1]
      labels  : tf.int32 tensor of shape [?]
    Returns:
      image   : preprocessed image
                  tf.float32 tensor of shape [32, ?, 1] (? = width)
      width   : width (in pixels) of image
                  tf.int32 tensor of shape []
      labels  : list of indices (+1) of characters mapping text->out_charset
                  tf.int32 tensor of shape [?] (? = length)
      length  : length of labels
                  tf.int64 tensor of shape []
      text    : ground truth string
                  tf.string tensor of shape []
    """
    image = _preprocess_image( image )

    # Width is the 2nd element of the image tuple
    width = tf.size( image[1] ) 

    # Length length of labels/caption
    length = tf.size(labels)

    text = caption

    return image, width, labels, length, text


def postbatch_fn( image, width, label, length, text ):
    """ 
    Prepare dataset for ingestion by Estimator.
    Sparsifies and decrements labels, and 'packs' the rest of the components
    into feature map
    """

    # Labels must be sparse for ctc functions (loss, decoder, etc)
    # Convert dense to sparse with EOS token of 0
    label = tf.contrib.layers.dense_to_sparse( label, eos_token=0 )

    # Reconstruct sparse tensor, un-incrementing label values after conversion
    label = tf.SparseTensor( indices=label.indices,
                             values=tf.subtract(label.values,1), # decrement
                             dense_shape=label.dense_shape )
    
    # Format relevant features for estimator ingestion
    features = {
        "image" : image, 
        "width" : width,
        "length": length,
        "text"  : text
    }

    return features, label


def element_length_fn( image, width, label, length, text ):
    """ 
    Determine element length
    Note: mjsynth version of this function has an extra parameter (filename)
    """
    return width


def _preprocess_image( image ):
    """Rescale image"""
    image = pipeline.rescale_image( image )

    return image
