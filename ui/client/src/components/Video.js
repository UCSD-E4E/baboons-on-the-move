import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from "react-router-dom";
import { ShapeEditor, DrawLayer, wrapShape } from 'react-shape-editor';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import sampleLabels from './sample_labels.json';

const Video = () => {
  const videoPath = useLocation().state.path;
  const DESIRED_VIDEO_WIDTH = 1400;
  const vidRef = useRef();
  const timestampWatcherRef = useRef();
  const [focusedBaboon, setFocusedBaboon] = useState(0);
  const [{ vectorHeight, vectorWidth }, setVectorDimensions] = useState({
    vectorHeight: 0,
    vectorWidth: 0,
  });
  const [videoDuration, setVideoDuration] = useState(0);
  const [fps, setFps] = useState(30);
  const frameLength = 1 / fps;
  const maxFrames = Math.ceil(videoDuration / frameLength);
  const scale = DESIRED_VIDEO_WIDTH / (vectorWidth || 1);

  let idIterator = 1;
  const [frameItems, setFrameItems] = useState(sampleLabels);
  const [frameIndex, setFrameIndex] = useState(0);

  let isActualFrameItems = true;
  let mostRecentItems = frameItems[frameIndex] || [];
  if (mostRecentItems.length === 0) {
    for (let i = frameIndex - 1; i >= 0; i -= 1) {
      const items = frameItems[i];
      if (items && items.length > 0) {
        mostRecentItems = items;
        isActualFrameItems = false;
        break;
      }
    }
  }

  const constrainMove = ({ x, y, width, height, vectorHeight, vectorWidth }) => {
    return {
      x: Math.round(Math.min(vectorWidth - width, Math.max(0, x))),
      y: Math.round(Math.min(vectorHeight - height, Math.max(0, y))),
    };
  };

  const constrainResize = ({
    movingCorner: { x: movingX, y: movingY },
    vectorHeight,
    vectorWidth,
  }) => {
    return {
      x: Math.round(Math.min(vectorWidth, Math.max(0, movingX))),
      y: Math.round(Math.min(vectorHeight, Math.max(0, movingY))),
    };
  };

  function arrayReplace(arr, index, item) {
    return [
      ...arr.slice(0, index),
      ...(Array.isArray(item) ? item : [item]),
      ...arr.slice(index + 1),
    ];
  }

  const RectShape = wrapShape(({ width, height, isActual }) => {
    const color = isActual ? '0,0,255' : '0,0,0';
    return (
      <rect
        width={width}
        height={height}
        fill={`rgba(${color},0.2)`}
        stroke={`rgba(${color},0.8)`}
      />
    );
  });

  const setThisFrameItems = fn => {
    setFrameItems(prevFrameItems => {
      const nextFrameItems = prevFrameItems.concat();
      nextFrameItems[frameIndex] = fn(mostRecentItems);
      // console.log(JSON.stringify(nextFrameItems));
      return nextFrameItems;
    });
  };

  const getFrameIndex = timeSec => {
    return Math.floor(timeSec / frameLength);
  };

  const shapes = mostRecentItems.map((item, index) => {
    const { id, height, width, x, y } = item;
    return (
      <RectShape
        key={id}
        shapeId={id}
        shapeIndex={index}
        height={height}
        width={width}
        x={x}
        y={y}
        isActual={isActualFrameItems}
        onChange={newRect => {
          setThisFrameItems(currentItems =>
            arrayReplace(currentItems, index, {
              ...item,
              ...newRect,
            })
          );
        }}
        onDelete={() => {
          setThisFrameItems(currentItems =>
            arrayReplace(currentItems, index, [])
          );
          if(focusedBaboon>0){setFocusedBaboon(focusedBaboon - 1)}
        }}
        // onFocus={() => {setFocusedBaboon(index)}}
        constrainMove={constrainMove}
        constrainResize={constrainResize}
      />
    );
  });

  const updateFrameIndex = () => {
    const nextFrameIndex = getFrameIndex(vidRef.current.currentTime);
    if (nextFrameIndex !== frameIndex) {
      setFrameIndex(nextFrameIndex);
    }
  };

  const stopTracking = () => {
    cancelAnimationFrame(timestampWatcherRef.current);
  };

  const startTracking = () => {
    timestampWatcherRef.current = requestAnimationFrame(() => {
      updateFrameIndex();
      startTracking();
    });
  };

  const jumpToFrame = index => {
    const fixed = (maxFrames + index) % maxFrames;
    vidRef.current.currentTime = frameLength * (fixed + 0.001);
  };

  const changeFps = () => {
    const result = prompt(
      'Change the FPS? (note: time offset issues will occur with existing boxes)',
      String(fps)
    );
    if (result === null || result.trim().length < 1 || Number.isNaN(parseFloat(result))) {
      return;
    }
    setFps(parseFloat(result));
  };

  const handleBaboonSwitch = (event, nextBaboon) => {
    setFocusedBaboon(nextBaboon);
  };

  const getBaboonString = (b, num) => {
    const x2 = b.x + b.width;
    const y2 = b.y + b.height;
    return 'Baboon '+(num+1)+': ('+b.x+', '+b.y+'), ('+x2+', '+y2+')';
  };

  useEffect(() => {
    const keyboardHandler = e => {
      let handled = true;
      switch (e.key) {
        case 'a':
          jumpToFrame(frameIndex - 1);
          break;
        case 'd':
          jumpToFrame(frameIndex + 1);
          break;
        default:
          handled = false;
      }

      if (handled) {
        e.preventDefault();
      }
    };

    window.addEventListener('keydown', keyboardHandler);
    return () => window.removeEventListener('keydown', keyboardHandler);
  });

  return (
    <div>
      <video
        style={{position: 'absolute',top: 50,left: 50}}
        ref={vidRef}
        width={vectorWidth * scale}
        height={vectorHeight * scale}
        id="video"
        onLoadedMetadata={e => {
          // Set a listener to get the video's true dimensions when it loads
          setVectorDimensions({
            vectorWidth: e.target.videoWidth,
            vectorHeight: e.target.videoHeight,
          });
          setVideoDuration(e.target.duration);
        }}
        onTimeUpdate={updateFrameIndex}
        onPlay={() => {
          startTracking();
        }}
        onPause={() => {
          stopTracking();
          jumpToFrame(frameIndex);
        }}
        onWaiting={stopTracking}
        onPlaying={startTracking}
        controls={true}
      >
        <source src={videoPath} />
      </video>

      <ShapeEditor
        style={{position: 'absolute',top: 50,left: 50}}
        vectorWidth={vectorWidth*9/10}
        vectorHeight={vectorHeight*9/10}
        scale={scale}
      >
        <DrawLayer
          onAddShape={({ x, y, width, height }) => {
            setThisFrameItems(currentItems => [
              ...currentItems,
              { id: `id${idIterator}`, x, y, width, height },
            ]);
            setFocusedBaboon(frameItems[frameIndex].length);
            idIterator += 1;
          }}
          constrainMove={constrainMove}
          constrainResize={constrainResize}
        />
        {shapes}
      </ShapeEditor> 

      <Grid container style={{paddingTop: '5vh'}}>
        <Grid item xs={9}>
          <div width='100%' height='100%'></div>
        </Grid>

        <Grid item xs={3}>
          <Grid container spacing={6}>
            <Grid item xs={12}>
              <ToggleButtonGroup
                orientation="vertical"
                value={focusedBaboon}
                exclusive
                onChange={handleBaboonSwitch}
              >
                {frameItems[frameIndex].map((b, number) => (
                  <ToggleButton key={number} value={number}>{getBaboonString(b, number)}</ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Grid>

            <Grid item xs={12}>
              <Button variant="outlined" onClick={changeFps}>
                {fps} FPS
              </Button>
            </Grid>

            <Grid item xs={12}>
              <h5>Frame</h5>
              <Button title="Back one frame (a key)" onClick={() => jumpToFrame(frameIndex - 1)}>
                <h4>&lt;</h4>
              </Button>
              <input type="number" min={-1} max={maxFrames} step={1} value={frameIndex}
                onChange={e => jumpToFrame(e.target.value !== '' ? parseInt(e.target.value, 10) : 0)}
              />
              <Button title="Forward one frame (d key)" onClick={() => jumpToFrame(frameIndex + 1)}>
                <h4>&gt;</h4>
              </Button>
            </Grid>
          </Grid>
        </Grid>

      </Grid>
    </div>
  );
};

export default Video;
