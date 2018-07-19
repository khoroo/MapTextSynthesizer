#include "mtsynth/map_text_synthesizer.hpp"
#include "mts_implementation.hpp"

using namespace std;

MapTextSynthesizer::MapTextSynthesizer(){}

Ptr<MapTextSynthesizer> MapTextSynthesizer::create(){
    Ptr<MapTextSynthesizer> mts(new MTSImplementation());
    return mts;
}
/*
MapTextSynthesizer* MapTextSynthesizer::create(){
    MapTextSynthesizer* mts = new MTSImplementation();
    return mts;
}
*/
