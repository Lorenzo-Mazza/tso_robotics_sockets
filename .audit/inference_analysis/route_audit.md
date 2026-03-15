# ZMQ Route/Key Audit

Audit of all routes, request keys, and response keys used across all production
ZMQ server/client implementations, compared against `tso_robotics_sockets.constants`.

---

## 1. Current `tso_robotics_sockets.constants`

**File:** `/home/mazzalore/PycharmProjects/tso-robotics-sockets/src/tso_robotics_sockets/constants.py`

### ServerRoute
| Enum member       | String value         |
|--------------------|----------------------|
| TASK_STATUS        | `"task_status"`      |
| GET_OBSERVATION    | `"get_observation"`  |
| SEND_ACTION        | `"send_action"`      |
| REGISTER_CLIENT    | `"register_client"`  |
| COMPUTE_STEREO     | `"compute_stereo"`   |

### ServerStatus
| Enum member     | String value        |
|------------------|---------------------|
| FINISHED         | `"FINISHED"`        |
| ERROR            | `"ERROR"`           |
| PROCESSING       | `"PROCESSING"`      |
| WAITING_ACTION   | `"WAITING_ACTION"`  |
| CREATING_ENV     | `"CREATING_ENV"`    |

### RequestKey
| Enum member                  | String value                          |
|-------------------------------|---------------------------------------|
| ROUTE_NAME                    | `"route_name"`                        |
| TASK_ID                       | `"task_id"`                           |
| REQUEST_DISPARITY             | `"request_disparity"`                 |
| REQUEST_DEPTH                 | `"request_depth"`                     |
| REQUEST_POINT_CLOUD           | `"request_point_cloud"`               |
| REQUEST_GRIPPER_STATE         | `"request_gripper_state"`             |
| REQUEST_RECTIFIED_IMAGES      | `"request_rectified_images"`          |
| REQUEST_OBS_CAMERA_FRAME      | `"request_observation_camera_frame"`  |
| REQUEST_OBS_ROBOT_FRAME       | `"request_observation_robot_frame"`   |
| REQUEST_LANGUAGE_INSTRUCTION  | `"request_language_instruction"`      |
| ROBOT_ACTION                  | `"robot_action"`                      |
| GRIPPER_ACTION                | `"gripper_action"`                    |
| CAMERA_FRAME                  | `"camera_frame"`                      |
| COMPRESSION_TYPE              | `"compression_type"`                  |

### ResponseKey
| Enum member            | String value              |
|-------------------------|---------------------------|
| STATUS                  | `"status"`                |
| ERROR_MSG               | `"error_msg"`             |
| RESULT                  | `"result"`                |
| TASK_ID                 | `"task_id"`               |
| HEIGHT                  | `"height"`                |
| WIDTH                   | `"width"`                 |
| LEFT_IMG_RECTIFIED      | `"left_img_rectified"`    |
| LEFT_IMG                | `"left_img"`              |
| RIGHT_IMG_RECTIFIED     | `"right_img_rectified"`   |
| RIGHT_IMG               | `"right_img"`             |
| COMPRESSION_TYPE        | `"compression_type"`      |
| DISPARITY_MAP           | `"disparity_map"`         |
| DEPTH_MAP               | `"depth_map"`             |
| POINT_CLOUD             | `"point_cloud"`           |
| STEREO_COMPRESSION_TYPE | `"stereo_compression_type"` |
| ROBOT_STATE             | `"robot_state"`           |
| GRIPPER_STATE           | `"gripper_state"`         |
| LANGUAGE_INSTRUCTION    | `"language_instruction"`  |

---

## 2. Legacy `imitation_learning_toolkit.sockets.flags`

**File:** `/home/mazzalore/miniforge3/envs/versatil/lib/python3.11/site-packages/imitation_learning_toolkit/sockets/flags.py`

This is the old package that `tso_robotics_sockets` replaces. All enums are 1:1 copies
except for:

| Old (il_toolkit)                | New (tso_robotics_sockets)   | Notes                     |
|----------------------------------|-------------------------------|---------------------------|
| `Routes.SUM`                    | --                            | Example route, not ported |
| `Routes.SUBTRACT`              | --                            | Example route, not ported |
| `RequestKeys.REQUEST_LANGUAGE_INSTRUCTION` | --               | **MISSING in il_toolkit** |
| `ResponseKeys.LANGUAGE_INSTRUCTION`        | --               | **MISSING in il_toolkit** |

The il_toolkit flags.py has **no** `REQUEST_LANGUAGE_INSTRUCTION` or `LANGUAGE_INSTRUCTION`.
The `model_robot_pose_setter.py` imports from il_toolkit but accesses `RequestKeys.REQUEST_LANGUAGE_INSTRUCTION`
-- this member does **not** exist in the shipped il_toolkit. It must be a locally patched version
or the import would fail at runtime. The `tso_robotics_sockets.constants` correctly includes both.

---

## 3. Per-File Audit

### 3.1 VersatIL SimulationClient (simulation servers protocol)

**File:** `/home/mazzalore/PycharmProjects/Surg-IL/src/versatil/inference/simulation_client.py`

Uses its **own local enums** (not importing from either sockets package):

| Category       | Key                             | String value                  | In tso_robotics_sockets? |
|----------------|---------------------------------|-------------------------------|--------------------------|
| Route          | `ServerRoute.GET_OBSERVATION`   | `"get_observation"`           | YES                      |
| Route          | `ServerRoute.SEND_ACTION`       | `"send_action"`               | YES                      |
| Route          | `ServerRoute.REGISTER_CLIENT`   | `"register_client"`           | YES                      |
| Request key    | `REQUESTED_KEYS`                | `"requested_keys"`            | **NO**                   |
| Request key    | `ACTIONS`                       | `"actions"`                   | **NO**                   |
| Request key    | `CLIENT_NAME`                   | `"client_name"`               | **NO**                   |
| Request key    | `COMPRESSION_TYPE`              | `"compression_type"`          | YES                      |
| Response key   | `STATUS`                        | `"status"`                    | YES                      |
| Response key   | `ERROR_MSG`                     | `"error_msg"`                 | YES                      |
| Response key   | `RESET_ENVIRONMENT_INDICES`     | `"reset_environment_indices"` | **NO**                   |
| Response key   | `TIMESTEP`                      | `"timestep"`                  | **NO**                   |
| Response key   | `IMAGE_HEIGHT`                  | `"image_height"`              | **NO** (has `"height"`)  |
| Response key   | `IMAGE_WIDTH`                   | `"image_width"`               | **NO** (has `"width"`)   |
| Status         | `FINISHED`                      | `"FINISHED"`                  | YES                      |
| Status         | `ERROR`                         | `"ERROR"`                     | YES                      |
| Status         | `WAITING_ACTION`                | `"WAITING_ACTION"`            | YES                      |
| Status         | `PROCESSING`                    | `"PROCESSING"`                | YES                      |
| Status         | `CREATING_ENV`                  | `"CREATING_ENV"`              | YES                      |

**Observation data keys are dynamic** -- they come from the policy's `observation_space` metadata
(e.g., `"agentview_rgb"`, `"ee_pos_action"`, `"language_instruction"`, etc.). These are
domain-specific, not wire protocol constants.

### 3.2 VersatIL TSOPolicyClient (real robot protocol)

**File:** `/home/mazzalore/PycharmProjects/Surg-IL/src/versatil/inference/tso_client.py`

Extends `AbstractModelClient` from `imitation_learning_toolkit.sockets.model_client`.
Uses the il_toolkit flags indirectly through `AbstractModelClient.get_observation()` and
`AbstractModelClient.send_action()`.

**Routes used (via AbstractModelClient):**
| Route                  | String value         | In tso_robotics_sockets? |
|------------------------|----------------------|--------------------------|
| `Routes.GET_OBSERVATION` | `"get_observation"` | YES                      |
| `Routes.SEND_ACTION`    | `"send_action"`     | YES                      |

**Request keys sent (via AbstractModelClient.get_observation):**
| Key                          | String value                          | In tso_robotics_sockets? |
|-------------------------------|---------------------------------------|--------------------------|
| `REQUEST_DISPARITY`           | `"request_disparity"`                 | YES                      |
| `REQUEST_DEPTH`               | `"request_depth"`                     | YES                      |
| `REQUEST_POINT_CLOUD`         | `"request_point_cloud"`               | YES                      |
| `REQUEST_GRIPPER_STATE`       | `"request_gripper_state"`             | YES                      |
| `REQUEST_RECTIFIED_IMAGES`    | `"request_rectified_images"`          | YES                      |
| `REQUEST_OBS_ROBOT_FRAME`     | `"request_observation_robot_frame"`   | YES                      |
| `REQUEST_OBS_CAMERA_FRAME`    | `"request_observation_camera_frame"`  | YES                      |
| `COMPRESSION_TYPE`            | `"compression_type"`                  | YES                      |

**Request keys sent (via AbstractModelClient.send_action):**
| Key               | String value       | In tso_robotics_sockets? |
|--------------------|---------------------|--------------------------|
| `ROBOT_ACTION`     | `"robot_action"`    | YES                      |
| `GRIPPER_ACTION`   | `"gripper_action"`  | YES                      |
| `CAMERA_FRAME`     | `"camera_frame"`    | YES                      |

**Response keys read (via AbstractModelClient.get_observation):**
| Key                       | String value              | In tso_robotics_sockets? |
|----------------------------|---------------------------|--------------------------|
| `STATUS`                   | `"status"`                | YES                      |
| `COMPRESSION_TYPE`         | `"compression_type"`      | YES                      |
| `LEFT_IMG_RECTIFIED`       | `"left_img_rectified"`    | YES                      |
| `LEFT_IMG`                 | `"left_img"`              | YES                      |
| `RIGHT_IMG_RECTIFIED`      | `"right_img_rectified"`   | YES                      |
| `RIGHT_IMG`                | `"right_img"`             | YES                      |
| `ROBOT_STATE`              | `"robot_state"`           | YES                      |
| `STEREO_COMPRESSION_TYPE`  | `"stereo_compression_type"` | YES                    |
| `DISPARITY_MAP`            | `"disparity_map"`         | YES                      |
| `DEPTH_MAP`                | `"depth_map"`             | YES                      |
| `POINT_CLOUD`              | `"point_cloud"`           | YES                      |
| `GRIPPER_STATE`            | `"gripper_state"`         | YES                      |

**Note:** `TSOPolicyClient` also passes `request_language_instruction=self.use_language`
to `AbstractModelClient.__init__()`, but the `AbstractModelClient` in il_toolkit does NOT
send or handle language instructions at all. The language param is used only by the
`model_robot_pose_setter` on the server side. This is a known gap in the il_toolkit.

### 3.3 ModelPoseSetter (real robot server)

**File:** `/home/mazzalore/robot_testbed/src/input_devices/intermediate_nodes/scripts/model_robot_pose_setter.py`

Imports from `imitation_learning_toolkit.sockets.flags` (Routes, RequestKeys, ResponseKeys, Status).

**Routes registered:**
| Route                     | String value         | In tso_robotics_sockets? |
|----------------------------|----------------------|--------------------------|
| `Routes.GET_OBSERVATION`   | `"get_observation"`  | YES                      |
| `Routes.SEND_ACTION`       | `"send_action"`      | YES                      |

**Routes used as client (to depth server):**
| Route                     | String value         | In tso_robotics_sockets? |
|----------------------------|----------------------|--------------------------|
| `Routes.COMPUTE_STEREO`   | `"compute_stereo"`   | YES                      |

**Request keys READ (from incoming client requests):**
| Key                              | String value                          | In tso_robotics_sockets? |
|-----------------------------------|---------------------------------------|--------------------------|
| `ROUTE_NAME`                      | `"route_name"`                        | YES                      |
| `REQUEST_DISPARITY`               | `"request_disparity"`                 | YES                      |
| `REQUEST_DEPTH`                   | `"request_depth"`                     | YES                      |
| `REQUEST_POINT_CLOUD`             | `"request_point_cloud"`               | YES                      |
| `REQUEST_GRIPPER_STATE`           | `"request_gripper_state"`             | YES                      |
| `REQUEST_RECTIFIED_IMAGES`        | `"request_rectified_images"`          | YES                      |
| `REQUEST_LANGUAGE_INSTRUCTION`    | `"request_language_instruction"`      | YES                      |
| `REQUEST_OBS_CAMERA_FRAME`        | `"request_observation_camera_frame"`  | YES                      |
| `REQUEST_OBS_ROBOT_FRAME`         | `"request_observation_robot_frame"`   | YES                      |
| `COMPRESSION_TYPE`                | `"compression_type"`                  | YES                      |
| `ROBOT_ACTION`                    | `"robot_action"`                      | YES                      |
| `GRIPPER_ACTION`                  | `"gripper_action"`                    | YES                      |
| `CAMERA_FRAME`                    | `"camera_frame"`                      | YES                      |

**Request keys SENT (to depth server):**
| Key                | String value         | In tso_robotics_sockets? |
|---------------------|----------------------|--------------------------|
| `COMPRESSION_TYPE`  | `"compression_type"` | YES                      |
| `REQUEST_DISPARITY` | `"request_disparity"`| YES                      |
| `REQUEST_DEPTH`     | `"request_depth"`    | YES                      |
| `REQUEST_POINT_CLOUD` | `"request_point_cloud"` | YES                 |

Also sends `ResponseKeys.LEFT_IMG` and `ResponseKeys.RIGHT_IMG` as request payload keys
to the depth server (used as data, not protocol keys).

**Response keys WRITTEN:**
| Key                       | String value              | In tso_robotics_sockets? |
|----------------------------|---------------------------|--------------------------|
| `LEFT_IMG_RECTIFIED`       | `"left_img_rectified"`    | YES                      |
| `LEFT_IMG`                 | `"left_img"`              | YES                      |
| `RIGHT_IMG_RECTIFIED`      | `"right_img_rectified"`   | YES                      |
| `RIGHT_IMG`                | `"right_img"`             | YES                      |
| `ROBOT_STATE`              | `"robot_state"`           | YES                      |
| `DISPARITY_MAP`            | `"disparity_map"`         | YES                      |
| `DEPTH_MAP`                | `"depth_map"`             | YES                      |
| `POINT_CLOUD`              | `"point_cloud"`           | YES                      |
| `STEREO_COMPRESSION_TYPE`  | `"stereo_compression_type"` | YES                    |
| `GRIPPER_STATE`            | `"gripper_state"`         | YES                      |
| `COMPRESSION_TYPE`         | `"compression_type"`      | YES                      |
| `ERROR_MSG`                | `"error_msg"`             | YES                      |
| `LANGUAGE_INSTRUCTION`     | `"language_instruction"`  | YES                      |

### 3.4 MockDepthServer

**File:** `/home/mazzalore/robot_testbed/src/input_devices/intermediate_nodes/scripts/mock_depth_server.py`

**Route handled:**
| Route                   | String value       | In tso_robotics_sockets? |
|--------------------------|--------------------|--------------------------|
| `Routes.COMPUTE_STEREO`  | `"compute_stereo"` | YES                      |

**Request keys read:**
| Key                | String value         | In tso_robotics_sockets? |
|---------------------|----------------------|--------------------------|
| `ROUTE_NAME`        | `"route_name"`       | YES                      |
| `COMPRESSION_TYPE`  | `"compression_type"` | YES                      |

**Response keys written:**
| Key                | String value         | In tso_robotics_sockets? |
|---------------------|----------------------|--------------------------|
| `STATUS`            | `"status"`           | YES                      |
| `ERROR_MSG`         | `"error_msg"`        | YES                      |
| `DISPARITY_MAP`     | `"disparity_map"`    | YES                      |
| `DEPTH_MAP`         | `"depth_map"`        | YES                      |
| `COMPRESSION_TYPE`  | `"compression_type"` | YES                      |

### 3.5 OfflineValidationServer

**File:** `/home/mazzalore/PycharmProjects/Surg-IL/offline_validation_server.py`

Uses its **own local enums** (not importing from tso_robotics_sockets). The protocol
is LIBERO-style but self-contained.

**Routes registered:**
| Route                          | String value         | In tso_robotics_sockets? |
|---------------------------------|----------------------|--------------------------|
| `LiberoRoutes.GET_OBSERVATION`  | `"get_observation"`  | YES                      |
| `LiberoRoutes.SEND_ACTION`      | `"send_action"`      | YES                      |
| `LiberoRoutes.RESET_EPISODE`    | `"reset_episode"`    | **NO**                   |

**Request keys read:**
| Key                             | String value                 | In tso_robotics_sockets? |
|----------------------------------|------------------------------|--------------------------|
| `ROUTE_NAME`                     | `"route_name"`               | YES                      |
| `ROBOT_ACTION`                   | `"robot_action"`             | YES                      |
| `EPISODE_IDX`                    | `"episode_idx"`              | **NO**                   |
| `REQUEST_AGENTVIEW`              | `"request_agentview_rgb"`    | **NO**                   |
| `REQUEST_EYE_IN_HAND`            | `"request_eye_in_hand_rgb"`  | **NO**                   |
| `REQUEST_EE_POS`                 | `"request_ee_pos"`           | **NO**                   |
| `REQUEST_EE_ORI`                 | `"request_ee_ori"`           | **NO**                   |
| `REQUEST_GRIPPER_STATES`         | `"request_gripper_states"`   | **NO**                   |
| `REQUEST_LANGUAGE_INSTRUCTION`   | `"request_language_instruction"` | YES                  |
| `COMPRESSION_TYPE`               | `"compression_type"`         | YES                      |

**Response keys written:**
| Key                      | String value              | In tso_robotics_sockets? |
|---------------------------|---------------------------|--------------------------|
| `STATUS`                  | `"status"`                | YES                      |
| `TIMESTEP`                | `"timestep"`              | **NO**                   |
| `MAX_TIMESTEPS`           | `"max_timesteps"`         | **NO**                   |
| `DONE`                    | `"done"`                  | **NO**                   |
| `SUCCESS`                 | `"success"`               | **NO**                   |
| `REWARD`                  | `"reward"`                | **NO**                   |
| `COMPRESSION_TYPE`        | `"compression_type"`      | YES                      |
| `IMAGE_HEIGHT`            | `"image_height"`          | **NO** (has `"height"`)  |
| `IMAGE_WIDTH`             | `"image_width"`           | **NO** (has `"width"`)   |
| `AGENTVIEW_RGB`           | `"agentview_rgb"`         | **NO**                   |
| `EYE_IN_HAND_RGB`         | `"eye_in_hand_rgb"`       | **NO**                   |
| `EE_POS`                  | `"ee_pos"`                | **NO**                   |
| `EE_ORI`                  | `"ee_ori"`                | **NO**                   |
| `GRIPPER_STATES`          | `"gripper_states"`        | **NO**                   |
| `LANGUAGE_INSTRUCTION`    | `"language_instruction"`  | YES                      |
| `ERROR_MSG`               | `"error_msg"`             | YES                      |

### 3.6 Libero-Plus Server

**File:** `/home/mazzalore/PycharmProjects/libero-plus/versatil_inference/server.py`
**Flags:** `/home/mazzalore/PycharmProjects/libero-plus/versatil_inference/socket_flags.py`

Uses the **simulation server protocol** (multi-env, requested_keys pattern).

**Routes registered:**
| Route                          | String value         | In tso_robotics_sockets? |
|---------------------------------|----------------------|--------------------------|
| `LiberoRoute.GET_OBSERVATION`   | `"get_observation"`  | YES                      |
| `LiberoRoute.SEND_ACTION`       | `"send_action"`      | YES                      |
| `LiberoRoute.REGISTER_CLIENT`   | `"register_client"`  | YES                      |

**Request keys read:**
| Key                | String value         | In tso_robotics_sockets? |
|---------------------|----------------------|--------------------------|
| `ROUTE_NAME`        | `"route_name"`       | YES                      |
| `REQUESTED_KEYS`    | `"requested_keys"`   | **NO**                   |
| `ACTIONS`           | `"actions"`          | **NO**                   |
| `CLIENT_NAME`       | `"client_name"`      | **NO**                   |
| `COMPRESSION_TYPE`  | `"compression_type"` | YES                      |

**Response keys written:**
| Key                           | String value                  | In tso_robotics_sockets? |
|--------------------------------|-------------------------------|--------------------------|
| `STATUS`                       | `"status"`                    | YES                      |
| `ERROR_MSG`                    | `"error_msg"`                 | YES                      |
| `RESET_ENVIRONMENT_INDICES`    | `"reset_environment_indices"` | **NO**                   |
| `TIMESTEP`                     | `"timestep"`                  | **NO**                   |
| `IMAGE_HEIGHT`                 | `"image_height"`              | **NO** (has `"height"`)  |
| `IMAGE_WIDTH`                  | `"image_width"`               | **NO** (has `"width"`)   |

**Observation data keys (dynamic, sent as response values):**
| Key                       | String value                | In tso_robotics_sockets? |
|----------------------------|-----------------------------|--------------------------|
| `AGENTVIEW`                | `"agentview_rgb"`           | **NO** (domain-specific) |
| `EYE_IN_HAND`              | `"eye_in_hand_rgb"`         | **NO** (domain-specific) |
| `EE_POS_ACTION`            | `"ee_pos_action"`           | **NO** (domain-specific) |
| `EE_ORI_ACTION`            | `"ee_ori_action"`           | **NO** (domain-specific) |
| `GRIPPER_STATE_ACTION`     | `"gripper_state_action"`    | **NO** (domain-specific) |
| `LANGUAGE_INSTRUCTION`     | `"language_instruction"`    | YES                      |

### 3.7 Libero-Pro Server

**File:** `/home/mazzalore/PycharmProjects/libero-pro/versatil_inference/server.py`
**Flags:** `/home/mazzalore/PycharmProjects/libero-pro/versatil_inference/socket_flags.py`

Identical protocol to Libero-Plus (same routes, request keys, response keys, observation keys).

### 3.8 MetaWorld-Plus Server

**File:** `/home/mazzalore/PycharmProjects/metaworldplus/versatil_inference/server.py`
**Flags:** `/home/mazzalore/PycharmProjects/metaworldplus/versatil_inference/socket_flags.py`

**Routes registered:**
| Route                              | String value         | In tso_robotics_sockets? |
|--------------------------------------|----------------------|--------------------------|
| `MetaWorldRoute.GET_OBSERVATION`     | `"get_observation"`  | YES                      |
| `MetaWorldRoute.SEND_ACTION`         | `"send_action"`      | YES                      |
| `MetaWorldRoute.REGISTER_CLIENT`     | `"register_client"`  | YES                      |

**Request keys read:**
| Key                | String value         | In tso_robotics_sockets? |
|---------------------|----------------------|--------------------------|
| `ROUTE_NAME`        | `"route_name"`       | YES                      |
| `REQUESTED_KEYS`    | `"requested_keys"`   | **NO**                   |
| `ACTIONS`           | `"actions"`          | **NO**                   |
| `CLIENT_NAME`       | `"client_name"`      | **NO**                   |
| `COMPRESSION_TYPE`  | `"compression_type"` | YES                      |

**Response keys written:**
| Key                           | String value                  | In tso_robotics_sockets? |
|--------------------------------|-------------------------------|--------------------------|
| `STATUS`                       | `"status"`                    | YES                      |
| `ERROR_MSG`                    | `"error_msg"`                 | YES                      |
| `RESET_ENVIRONMENT_INDICES`    | `"reset_environment_indices"` | **NO**                   |
| `TIMESTEP`                     | `"timestep"`                  | **NO**                   |
| `IMAGE_HEIGHT`                 | `"image_height"`              | **NO** (has `"height"`)  |
| `IMAGE_WIDTH`                  | `"image_width"`               | **NO** (has `"width"`)   |

**Observation data keys:**
| Key                       | String value                | In tso_robotics_sockets? |
|----------------------------|-----------------------------|--------------------------|
| `AGENTVIEW`                | `"agentview_rgb"`           | **NO** (domain-specific) |
| `EE_POS_ACTION`            | `"ee_pos_action"`           | **NO** (domain-specific) |
| `GRIPPER_STATE_ACTION`     | `"gripper_state_action"`    | **NO** (domain-specific) |
| `LANGUAGE_INSTRUCTION`     | `"language_instruction"`    | YES                      |

### 3.9 NeedleThreading InferenceClient (legacy)

**File:** `/home/mazzalore/PycharmProjects/needlethreading_il/src/inference_client.py`

Extends `AbstractModelClient` from `imitation_learning_toolkit.sockets.model_client`.
Uses the same routes/keys as TSOPolicyClient (section 3.2) through the inherited
`get_observation()` and `send_action()` methods. No additional routes or keys introduced.

---

## 4. Gap Summary: Keys/Routes Missing from `tso_robotics_sockets.constants`

### Routes
| String value       | Used by                    | Notes                                       |
|---------------------|----------------------------|----------------------------------------------|
| `"reset_episode"`   | OfflineValidationServer    | Libero-specific, may not belong in core      |

### Request Keys
| String value           | Used by                                            |
|------------------------|----------------------------------------------------|
| `"requested_keys"`     | SimulationClient, Libero-Plus, Libero-Pro, MetaWorld |
| `"actions"`            | SimulationClient, Libero-Plus, Libero-Pro, MetaWorld |
| `"client_name"`        | SimulationClient, Libero-Plus, Libero-Pro, MetaWorld |
| `"episode_idx"`        | OfflineValidationServer only                        |
| `"request_agentview_rgb"` | OfflineValidationServer only                     |
| `"request_eye_in_hand_rgb"` | OfflineValidationServer only                  |
| `"request_ee_pos"`     | OfflineValidationServer only                        |
| `"request_ee_ori"`     | OfflineValidationServer only                        |
| `"request_gripper_states"` | OfflineValidationServer only                    |

### Response Keys
| String value                  | Used by                                            |
|-------------------------------|----------------------------------------------------|
| `"reset_environment_indices"` | SimulationClient, Libero-Plus, Libero-Pro, MetaWorld |
| `"timestep"`                  | SimulationClient, Libero-Plus, Libero-Pro, MetaWorld, OfflineValidationServer |
| `"image_height"`              | SimulationClient, Libero-Plus, Libero-Pro, MetaWorld, OfflineValidationServer |
| `"image_width"`               | SimulationClient, Libero-Plus, Libero-Pro, MetaWorld, OfflineValidationServer |
| `"max_timesteps"`             | OfflineValidationServer only                        |
| `"done"`                      | OfflineValidationServer only                        |
| `"success"`                   | OfflineValidationServer only                        |
| `"reward"`                    | OfflineValidationServer only                        |

**Note on `"height"` vs `"image_height"`:** The tso_robotics_sockets constants use `"height"` and `"width"`,
but all simulation servers (Libero-Plus, Libero-Pro, MetaWorld) and the SimulationClient use
`"image_height"` and `"image_width"`. This is a naming mismatch. The ModelPoseSetter (real robot)
does not send height/width at all, so the `"height"`/`"width"` values are unused in production.

---

## 5. Two Distinct Protocols

The audit reveals two clearly different wire protocols:

### Protocol A: Real Robot (TSO testbed)
Used by: ModelPoseSetter (server), TSOPolicyClient / NeedleThreading (clients), MockDepthServer.

- **No multi-env** -- single observation/action per request.
- Request keys use **boolean flags** to specify what to include (`request_depth`, `request_gripper_state`, etc.).
- Actions are structured: separate `robot_action` (4D array) + `gripper_action` (bool) + `camera_frame` (bool).
- Server returns raw image blobs keyed by `left_img`/`right_img`/`left_img_rectified`/`right_img_rectified`.
- Includes stereo pipeline: `COMPUTE_STEREO` route to depth server.
- **Fully covered** by `tso_robotics_sockets.constants`.

### Protocol B: Simulation Servers (Libero, MetaWorld)
Used by: SimulationClient (client), Libero-Plus/Libero-Pro/MetaWorld servers.

- **Multi-env** -- responses are dicts keyed by environment index.
- Request uses `requested_keys` list to specify which observation keys to include.
- Actions are sent as `actions` dict keyed by environment index.
- Uses `register_client` route with `client_name`.
- Server returns `reset_environment_indices`, `timestep`, `image_height`, `image_width`.
- Observation data keys are **domain-specific** (e.g., `agentview_rgb`, `ee_pos_action`).
- **Partially missing** from `tso_robotics_sockets.constants` -- the simulation protocol keys
  (`requested_keys`, `actions`, `client_name`, `reset_environment_indices`, `timestep`,
  `image_height`, `image_width`) are not present.

---

## 6. Recommendations

1. **Add simulation protocol keys** to `tso_robotics_sockets.constants`:
   - `RequestKey.REQUESTED_KEYS` = `"requested_keys"`
   - `RequestKey.ACTIONS` = `"actions"`
   - `RequestKey.CLIENT_NAME` = `"client_name"`
   - `ResponseKey.RESET_ENVIRONMENT_INDICES` = `"reset_environment_indices"`
   - `ResponseKey.TIMESTEP` = `"timestep"`
   - `ResponseKey.IMAGE_HEIGHT` = `"image_height"`
   - `ResponseKey.IMAGE_WIDTH` = `"image_width"`

2. **Reconcile height/width naming**: Either rename `HEIGHT`/`WIDTH` to `IMAGE_HEIGHT`/`IMAGE_WIDTH`
   or add both (the current `"height"`/`"width"` values appear unused by any production code).

3. **Domain-specific observation keys** (agentview_rgb, ee_pos_action, etc.) should remain in
   each project's own `socket_flags.py` -- they are not wire protocol constants but data schema keys.

4. **Migrate all consumers** off `imitation_learning_toolkit.sockets.flags` to import from
   `tso_robotics_sockets.constants` instead:
   - `model_robot_pose_setter.py` (robot_testbed)
   - `mock_depth_server.py` (robot_testbed)
   - `inference_client.py` (needlethreading_il, legacy -- uses AbstractModelClient which itself imports il_toolkit flags)
   - Libero-Plus, Libero-Pro, MetaWorld servers already use their own local flags -- these should
     import the shared protocol keys from `tso_robotics_sockets.constants`.

5. **OfflineValidationServer** keys (`reset_episode`, `episode_idx`, `done`, `success`, `reward`,
   `max_timesteps`) are specific to offline debugging and may not need to be in the shared constants.
