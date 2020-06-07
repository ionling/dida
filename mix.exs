defmodule Dida.MixProject do
  use Mix.Project

  def project do
    [
      app: :dida,
      version: "0.1.0",
      elixir: "~> 1.10",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      mod: {Dida, []},
      extra_applications: [:logger]
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:httpoison, "~> 1.6"},
      {:jason, "~> 1.2"},
      {:sqlitex, "~> 1.7"},
      {:tzdata, "~> 1.0.3"},
    ]
  end
end
