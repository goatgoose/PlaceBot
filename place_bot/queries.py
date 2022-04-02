
SET_PIXEL_QUERY = \
"""mutation setPixel($input: ActInput!) {
  act(input: $input) {
    data {
      ... on BasicMessage {
        id
        data {
          ... on GetUserCooldownResponseMessageData {
            nextAvailablePixelTimestamp
            __typename
          }
          ... on SetPixelResponseMessageData {
            timestamp
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
"""


FULL_FRAME_MESSAGE_SUBSCRIBE_QUERY = \
"""subscription replace($input: SubscribeInput!) {
  subscribe(input: $input) {
    id
    ... on BasicMessage {
      data {
        __typename
        ... on FullFrameMessageData {
          __typename
          name
          timestamp
        }
      }
      __typename
    }
    __typename
  }
}
"""
