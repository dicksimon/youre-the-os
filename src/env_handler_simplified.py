import gymnasium  as gym
from gymnasium.experimental.wrappers import FlattenObservationV0
from gymnasium.envs.registration import register
from stable_baselines3 import A2C
from stable_baselines3.common.env_util import make_vec_env

# Register the environment
gym.register(
    id='YOS-v0',
    entry_point='envs.yos_env_simplified:YosEnvSimplified',
    kwargs={'render_mode': 'human'}
)


env = gym.make("YOS-v0")
print (env.observation_space.shape)
env = FlattenObservationV0(env)
print (env.observation_space.shape)
obs = env.reset()

model = A2C("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
model.save("a2c_yos_env")
del model 
model = A2C.load("a2c_yos_env")



while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render("human")

